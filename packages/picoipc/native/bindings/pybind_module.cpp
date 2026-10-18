#include "smh_q/ring.hpp"
#include <pybind11/pybind11.h>
#include <memory>
#include <mutex>
#include <shared_mutex>
#include <span>
#include <string>
#include <type_traits>

namespace py = pybind11;

namespace {
struct RingState {
  RingState(smh_q::Ring::Config cfg, bool create)
      : name(cfg.name), ring(std::make_shared<smh_q::Ring>(std::move(cfg), create)) {}
  std::shared_mutex lifecycle;
  const std::string name;
  std::shared_ptr<smh_q::Ring> ring;
};

struct ClaimBuffer {
  ClaimBuffer(std::shared_ptr<smh_q::Ring> owner, std::span<std::byte> span)
      : owner(std::move(owner)), data(span.data()), size(span.size()) {}
  std::shared_ptr<smh_q::Ring> owner;
  std::byte* data;
  std::size_t size;
};

template <class Fn>
auto with_ring(const std::shared_ptr<RingState>& state, Fn&& fn) {
  py::gil_scoped_release release;
  std::shared_lock lock(state->lifecycle);
  auto owner = state->ring;
  return fn(std::move(owner));
}

py::buffer_info require_bytes_buffer(const py::buffer& buffer, bool writable) {
  auto info = buffer.request(false);
  if ((writable && info.readonly) || info.ndim != 1 || info.itemsize != 1 ||
      info.strides[0] != 1) {
    throw py::type_error("buffer must be contiguous 1-D byte storage");
  }
  return info;
}
}  // namespace

PYBIND11_MODULE(_native, m, py::mod_gil_not_used()) {
  m.doc() = "smh_q native Ring";
  py::class_<ClaimBuffer>(m, "_ClaimBuffer", py::buffer_protocol())
      .def_buffer([](ClaimBuffer& self) {
        return py::buffer_info(self.data, 1, "B", 1,
                               {static_cast<py::ssize_t>(self.size)}, {1}, false);
      });

  py::class_<RingState, std::shared_ptr<RingState>>(m, "Ring")
      .def(py::init([](const std::string& name, bool create, uint32_t slot_count,
                       uint32_t slot_size, uint16_t schema_id, uint16_t version, uint32_t magic) {
             smh_q::Ring::Config cfg;
             cfg.name = name;
             cfg.slot_count = slot_count;
             cfg.slot_size = slot_size;
             cfg.schema_id = schema_id;
             cfg.version = version;
             cfg.magic = magic == 0 ? smh_q::kDefaultMagic : magic;
             return std::make_shared<RingState>(std::move(cfg), create);
           }),
           py::arg("name") = "smh_q_demo", py::arg("create") = false,
           py::arg("slot_count") = 64, py::arg("slot_size") = 256,
           py::arg("schema_id") = 1, py::arg("version") = 1,
           py::arg("magic") = smh_q::kDefaultMagic)
      .def("try_publish", [](const std::shared_ptr<RingState>& state, py::object payload) {
        if (py::isinstance<py::bytes>(payload)) {
          char* data;
          py::ssize_t size;
          if (PyBytes_AsStringAndSize(payload.ptr(), &data, &size) < 0) throw py::error_already_set();
          return with_ring(state, [=](const auto& owner) {
            return owner && owner->try_publish({reinterpret_cast<const std::byte*>(data), static_cast<std::size_t>(size)});
          });
        }
        if (!py::isinstance<py::buffer>(payload)) throw py::type_error("try_publish expects bytes or buffer");
        auto info = require_bytes_buffer(py::buffer(payload), false);
        return with_ring(state, [&info](const auto& owner) {
          return owner && owner->try_publish({reinterpret_cast<const std::byte*>(info.ptr), static_cast<std::size_t>(info.size)});
        });
      })
      .def("claim", [](const std::shared_ptr<RingState>& state) -> py::object {
        auto result = with_ring(state, [](const auto& owner) {
          if (!owner) return std::pair<std::shared_ptr<smh_q::Ring>, std::span<std::byte>>{};
          return std::make_pair(owner, owner->claim());
        });
        if (result.second.empty()) return py::none();
        auto exporter = py::cast(ClaimBuffer(std::move(result.first), result.second));
        auto* view = PyMemoryView_FromObject(exporter.ptr());
        if (!view) throw py::error_already_set();
        return py::reinterpret_steal<py::object>(view);
      })
      .def("try_claim", [](const std::shared_ptr<RingState>& state) {
        return with_ring(state, [](const auto& owner) { return owner && !owner->claim().empty(); });
      })
      .def("publish", [](const std::shared_ptr<RingState>& state, std::size_t length) {
        return with_ring(state, [length](const auto& owner) {
          if (!owner) return false;
          if (owner->has_claim()) { owner->publish(length); return true; }
          return owner->try_publish_length(length);
        });
      })
      .def("publish", [](const std::shared_ptr<RingState>& state, py::buffer buf, std::size_t length) {
        auto info = require_bytes_buffer(buf, false);
        if (static_cast<std::size_t>(info.size) < length) throw std::runtime_error("publish buffer shorter than length");
        const bool open = with_ring(state, [&info, length](const auto& owner) {
          if (!owner) return false;
          owner->publish_payload({reinterpret_cast<const std::byte*>(info.ptr), length});
          return true;
        });
        if (!open) throw std::runtime_error("Ring is closed");
      }, py::arg("buf"), py::arg("length"))
      .def("try_consume_into", [](const std::shared_ptr<RingState>& state, py::buffer buf) -> py::object {
        auto info = require_bytes_buffer(buf, true);
        auto n = with_ring(state, [&info](const auto& owner) -> std::optional<std::size_t> {
          if (!owner) return std::nullopt;
          return owner->try_consume({reinterpret_cast<std::byte*>(info.ptr), static_cast<std::size_t>(info.size)});
        });
        if (!n) return py::none();
        return py::int_(*n);
      })
      .def("try_consume", [](const std::shared_ptr<RingState>& state) -> py::object {
        auto msg = with_ring(state, [](const auto& owner) -> std::optional<std::vector<std::byte>> {
          return owner ? owner->try_consume() : std::nullopt;
        });
        if (!msg) return py::none();
        return py::bytes(reinterpret_cast<const char*>(msg->data()), static_cast<py::ssize_t>(msg->size()));
      })
      .def("wait_readable", [](const std::shared_ptr<RingState>& state, int timeout_ms) {
        return with_ring(state, [timeout_ms](const auto& owner) {
          return owner && owner->wait_readable(std::chrono::milliseconds(timeout_ms));
        });
      })
      .def("wake", [](const std::shared_ptr<RingState>& state) {
        with_ring(state, [](const auto& owner) { if (owner) owner->wake(); });
      })
      .def("write_seq", [](const std::shared_ptr<RingState>& state) {
        return with_ring(state, [](const auto& owner) { return owner ? owner->write_seq() : uint32_t{0}; });
      })
      .def("read_seq", [](const std::shared_ptr<RingState>& state) {
        return with_ring(state, [](const auto& owner) { return owner ? owner->read_seq() : uint32_t{0}; });
      })
      .def("close", [](const std::shared_ptr<RingState>& state, bool unlink) {
        std::shared_ptr<smh_q::Ring> detached;
        {
          py::gil_scoped_release release;
          std::unique_lock lock(state->lifecycle);
          detached = std::move(state->ring);
        }
        detached.reset();
        if (unlink) smh_q::Ring::unlink(state->name);
      }, py::arg("unlink") = false)
      .def_static("unlink", &smh_q::Ring::unlink);
  m.def("unlink", &smh_q::Ring::unlink);
}
