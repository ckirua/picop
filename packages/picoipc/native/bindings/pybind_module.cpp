#include "smh_q/ring.hpp"
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <cstring>

namespace py = pybind11;

namespace {
std::vector<std::byte> bytes_to_vec(py::bytes b) {
  std::string s = b;
  std::vector<std::byte> out(s.size());
  if (!s.empty()) std::memcpy(out.data(), s.data(), s.size());
  return out;
}
}

PYBIND11_MODULE(_native, m, py::mod_gil_not_used()) {
  m.doc() = "smh_q native Ring";
  py::class_<smh_q::Ring>(m, "Ring")
      .def(py::init([](const std::string& name, bool create, uint32_t slot_count,
                       uint32_t slot_size, uint16_t schema_id, uint16_t version, uint32_t magic) {
             smh_q::Ring::Config cfg;
             cfg.name = name;
             cfg.slot_count = slot_count;
             cfg.slot_size = slot_size;
             cfg.schema_id = schema_id;
             cfg.version = version;
             cfg.magic = magic == 0 ? smh_q::kDefaultMagic : magic;
             return new smh_q::Ring(cfg, create);
           }),
           py::arg("name") = "smh_q_demo", py::arg("create") = false,
           py::arg("slot_count") = 64, py::arg("slot_size") = 256,
           py::arg("schema_id") = 1, py::arg("version") = 1,
           py::arg("magic") = smh_q::kDefaultMagic)
      .def("try_publish", [](smh_q::Ring& self, py::object payload) -> bool {
        if (py::isinstance<py::bytes>(payload)) {
          auto vec = bytes_to_vec(payload.cast<py::bytes>());
          return self.try_publish(std::span<const std::byte>(vec.data(), vec.size()));
        }
        if (py::isinstance<py::buffer>(payload)) {
          py::buffer_info info = py::buffer(payload).request(false);
          if (info.ndim != 1) {
            throw std::runtime_error("try_publish buffer must be 1-D");
          }
          return self.try_publish(std::span<const std::byte>(
              reinterpret_cast<const std::byte*>(info.ptr),
              static_cast<std::size_t>(info.size)));
        }
        throw py::type_error("try_publish expects bytes or buffer");
      })
      .def("claim", [](smh_q::Ring& self) -> py::object {
        auto slot = self.claim();
        if (slot.empty()) return py::none();
        return py::memoryview::from_memory(
            slot.data(), static_cast<py::ssize_t>(slot.size()));
      })
      .def("try_claim", [](smh_q::Ring& self) -> bool {
        return !self.claim().empty();
      })
      .def("publish", [](smh_q::Ring& self, std::size_t length) -> bool {
        if (self.has_claim()) {
          self.publish(length);
          return true;
        }
        return self.try_publish_length(length);
      })
      .def("publish", [](smh_q::Ring& self, py::buffer buf, std::size_t length) {
        py::buffer_info info = buf.request(false);
        if (info.ndim != 1) {
          throw std::runtime_error("publish buffer must be 1-D");
        }
        if (static_cast<std::size_t>(info.size) < length) {
          throw std::runtime_error("publish buffer shorter than length");
        }
        self.publish_payload(std::span<const std::byte>(
            reinterpret_cast<const std::byte*>(info.ptr), length));
      }, py::arg("buf"), py::arg("length"))
      .def("try_consume_into", [](smh_q::Ring& self, py::buffer buf) -> py::object {
        py::buffer_info info = buf.request(/*writable=*/true);
        if (info.ndim != 1) {
          throw std::runtime_error("try_consume_into buffer must be 1-D");
        }
        auto out = std::span<std::byte>(
            reinterpret_cast<std::byte*>(info.ptr),
            static_cast<std::size_t>(info.size));
        auto n = self.try_consume(out);
        if (!n) return py::none();
        return py::int_(*n);
      })
      .def("try_consume", [](smh_q::Ring& self) -> py::object {
        auto msg = self.try_consume();
        if (!msg) return py::none();
        return py::bytes(reinterpret_cast<const char*>(msg->data()),
                         static_cast<py::ssize_t>(msg->size()));
      })
      .def("wait_readable", [](smh_q::Ring& self, int timeout_ms) {
        return self.wait_readable(std::chrono::milliseconds(timeout_ms));
      })
      .def("wake", &smh_q::Ring::wake)
      .def("close", [](smh_q::Ring& self, bool unlink) {
        if (unlink) smh_q::Ring::unlink(self.name());
      }, py::arg("unlink") = false)
      .def_static("unlink", &smh_q::Ring::unlink);
  m.def("unlink", &smh_q::Ring::unlink);
}
