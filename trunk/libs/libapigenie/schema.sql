CREATE TABLE api_documentation (
  id            INT(11) auto_increment,
  documentation TEXT    NOT NULL DEFAULT ''
)

CREATE TABLE source_chunk (
  id         INT(11)      auto_increment,
  name       VARCHAR(255) DEFAULT NULL,
  data       VARCHAR(255) DEFAULT NULL,
  docs       INT(11)      REFERENCES api_documentation(id)
)

CREATE TABLE source_file (
  id       INT(11) auto_increment,
  chunk_id INT(11) REFERENCES chunk.id
)

CREATE TABLE api_class (
  id       INT(11) auto_increment,
  chunk_id INT(11) REFERENCES chunk.id
)

CREATE TABLE api_function (
  id INT(11)       auto_increment,
  chunk_id INT(11) REFERENCES chunk.id
)

CREATE TABLE variable (
  id       INT(11)      auto_increment,
  name     VARCHAR(100) DEFAULT NULL,
  var_type VARCHAR(100),
  docs     INT(11)      REFERENCES api_documentation(id)
)

CREATE TABLE api_function_argument_map (
  api_function_id INT(11) REFERENCES api_function.id,
  argument_id     INT(11) REFERENCES variable.id
)

CREATE TABLE api_function_return_map (
  api_function_id INT(11) REFERENCES api_function.id,
  return_id       INT(11) REFERENCES variable.id
)
