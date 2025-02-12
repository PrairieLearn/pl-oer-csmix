

npm install -p ./ @sqlite.org/sqlite-wasm
- This likely isn't needed or useful anymore, have a manual copy downloaded

<pl-file-editor file-name="here.sql" preview="sqlite" ace-mode="ace/mode/sql">select * from t;</pl-file-editor>

<pl-sqlite database="survey"></pl-sqlite>
<pl-sqlite-describe table="a"></pl-sqlite-describe>
<pl-sqlite-sandbox target-id="foo"></pl-sqlite-sandbox>



Load a database (first)
- potentially with a file

Run SQL, no output
- INSERT statements

Run SQL, show output
- special "describe these tables"
- Demos in the question
- Might be used with the sandbox (or share code)
- Submission or Answer panel

Sandbox with editor
- Edit in the web, run in JS (no reload), see the output
- Can be Save & Grade'd



<pl-sqlite>

  <execute>
  <display>
  <sandbox>
</pl-sqlite>

pl-checkbox
pl-multiplechoice
pl-orderblocks


.tables
(Lists tables)

.schema
(CREATE statements to recreate db)

.help
.mode column
.header on

.nullvalue foo

Some visible on screen history?

CodeMirror
https://codemirror.net/

SELECT name FROM my_db.sqlite_master WHERE type='table';

preload taking a data-source and getting its contents from there.

data-source ->   element.dataset.source

## Future use

Query output comparison

State of database

Random things



Airplane emoji
&#9992;&#65039;

pragma foreign_key_list('TableName');

Whitespace parser for queries to handle from HTML indentation, prettier?
