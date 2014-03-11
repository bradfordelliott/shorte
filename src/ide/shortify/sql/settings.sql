-- Global settings table containing settings for the entire ASIC
-- such as permissions or themes. Entries in this table can be
-- retrieved using the CS_GUI_GET_GLOBAL_SETTING
CREATE TABLE Settings
(
    -- A unique ID for the setting
    id INTEGER AUTO_INCREMENT,
    -- The unique key identifying the setting
    key TEXT,
    -- The value of the setting
    value TEXT,
    -- A text description of the setting
    description TEXT,
    PRIMARY KEY(id)
);

-- Remember paths of opened and saved files
INSERT INTO Settings (key,value) VALUES('path.last_saved', '');
INSERT INTO Settings (key,value) VALUES('path.last_opened', '');

-- ==========================================================
-- GUI THEMING
-- ==========================================================
-- @include "sql/theme.sql"

-- Populate the Lexer settings
@include "sql/lexers.sql"
