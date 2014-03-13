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
INSERT INTO Settings (key,value,description) VALUES('path.last_saved', '', 'The last path saved to');
INSERT INTO Settings (key,value,description) VALUES('path.last_opened', '', 'The last path opened from');

INSERT INTO Settings (key,value,description) VALUES('path.python', 'C:/usr/tools/python26/python.exe', 'The path to the python interpreter');
INSERT INTO Settings (key,value,description) VALUES('path.shorte', 'C:/usr/work/shorte/src/shorte.py', 'The path to the shorte command line');
INSERT INTO Settings (key,value,description) VALUES('env.pythonpath', 'C:\usr\tools\python26', 'The PYTHONPATH environment variable');
INSERT INTO Settings (key,value,description) VALUES('env.pythonhome', 'C:\usr\tools\python26', 'The PYTHONHOME environment variable');

-- INSERT INTO Settings (key,value,description) VALUES('path.python', '/usr/bin/python', 'The path to the python interpreter');
-- INSERT INTO Settings (key,value,description) VALUES('path.shorte', '/Users/belliott/usr/work/shorte/src/shorte.py', 'The path to the shorte command line');


-- ==========================================================
-- GUI THEMING
-- ==========================================================
@include "sql/theme.sql"

-- Populate the Lexer settings
@include "sql/lexers.sql"
