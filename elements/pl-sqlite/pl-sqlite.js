let db;
let queuedQueries = [];
let sandboxEditors = {};
let sandboxEditorsOrder = [];
let sqlite3;

const nullvalue = 'NULL';
const HIDE_COLUMNS_STARTING_WITH = '__';

async function setupsql(dburl) {
  if (db) {
    throw new Error('setupsql() already run, aborting');
  }
  sqlite3 = await sqlite3InitModule();
  console.log('Running SQLite3 version', sqlite3.version.libVersion);

  db = new sqlite3.oo1.DB();
  $('.sqlresult').html('Database ready.');

  if (dburl) {
    const response = await fetch(dburl);
    const buffer = await response.arrayBuffer();
    const bytes = new Uint8Array(buffer);

    const p = sqlite3.wasm.allocFromTypedArray(bytes);
    const rc = sqlite3.capi.sqlite3_deserialize(
      db.pointer,
      'main',
      p,
      bytes.byteLength,
      bytes.byteLength,
      sqlite3.capi.SQLITE_DESERIALIZE_RESIZEABLE
    );
    db.checkRc(rc);

    let tableCount = 0;
    let tableList = db.exec({
      sql: `select * from pragma_table_list where schema='main' and name != 'sqlite_schema'`,
      returnValue: 'resultRows',
    });

    $('.sqlresult').append(
      ` ${tableList.length} table${tableList.length === 1 ? '' : 's'} loaded.`
    );
  }

  console.log(queuedQueries);
  if (queuedQueries.length > 0) {
    queuedQueries.forEach(runsql);
    //$(".sqlresult").append(" Data loaded.");
  }
}

function runsql(query) {
  // Query object:
  // sql
  // output_id (can be missing or null)
  // summary
  // width?  full

  let sql = query.sql;

  let SR = document.getElementById(query.output_id);
  let tablebody;
  let table;
  let rowCount = 0;
  let special = {};

  try {
    if (!sql) {
      throw Error('No SQL provided.');
    }

    if (sql.trim() === '.show') {
      $('textarea.d-none').removeClass('d-none').addClass('d-block');
      return;
    }

    if (['.quit', '.exit'].includes(sql.trim())) {
      window.location.href = 'https://zombo.com/';
      return;
    }

    if (sql.trim() === '.help') {
      SR.innerText = `We support .help, .tables, .schema, .tableinfo tableName`;
      return;
    }

    if (sql.trim() === '.tables') {
      sql = `SELECT name FROM sqlite_master WHERE type='table';`;
    }

    if (sql.trim() === '.schema') {
      sql = `SELECT sql || ';' AS schema FROM sqlite_master WHERE type IN ('table', 'index');`;
      special['pre'] = true;
    }

    const tableInfo = sql.match(/^\.table[iI]nfo (\w+)\s*(\w+)?/);
    if (tableInfo) {
      let cols = '*';
      if (tableInfo[2] == 'brief') {
        cols = 'name, type, pk AS __pk';
        special['underline_pk'] = true;
      }
      sql = `SELECT ${cols} FROM pragma_table_info('${tableInfo[1]}');`;
    }

    if (SR) {
      SR.innerHTML = '';
      SR.style.border = '';
      SR.style.padding = '';
      //table = document.createElement("table");
      //SR.prepend(table);
      // Card accordian here?
      table = SR.appendChild(document.createElement('table'));
      table.classList.add('table', 'table-bordered', 'table-sm');

      if (query?.width != 'full') {
        table.classList.add('w-auto');
      }
    }

    db.exec({
      sql,
      callback: (result, Stmt) => {
        const columns = Stmt.getColumnNames();
        console.log(columns, result);

        if (!SR) return;

        if (rowCount == 0) {
          // First time let's setup the table
          let tablehead = table.createTHead();
          //tablehead.classList.add('thead-light');
          tablehead.classList.add('table-light');
          let row = tablehead.insertRow();
          for (let c of columns) {
            if (c.startsWith(HIDE_COLUMNS_STARTING_WITH)) {
              continue;
            }
            let newCell = row.appendChild(document.createElement('th'));
            newCell.textContent = c;
          }
          tablebody = table.createTBody();
        }
        let newrow = tablebody.insertRow();
        for (let [i, cell] of result.entries()) {
          if (columns[i].startsWith(HIDE_COLUMNS_STARTING_WITH)) {
            continue;
          }
          let newCell = newrow.insertCell();
          if (cell === null) {
            newCell.innerHTML = nullvalue;
            newCell.style.textAlign = 'center';
            newCell.style.color = 'darkgreen';
            newCell.style.fontWeight = 'bold';
            newCell.style.fontStyle = 'italic';
          } else if ('pre' in special) {
            const innerCode = document.createElement('code');
            innerCode.innerHTML = cell;
            innerCode.classList.add('language-sql');

            const pre = document.createElement('pre');
            pre.classList.add('p-0', 'm-0');
            pre.appendChild(innerCode);
            newCell.appendChild(pre);
          } else {
            newCell.textContent = cell;

            if ('underline_pk' in special && is_pk(i, result, columns)) {
              newCell.style.textDecoration = 'underline';
              //newCell.style.textDecorationColor = "green";
              const apx = document.createElement('span');
              newCell.title = 'primary key';
              apx.innerHTML = '&#x1f5dd;';
              apx.classList.add('float-right');
              newCell.append(apx);
            }
          }
        }
        rowCount++;
      },
    });

    if (SR && query.summary) {
      let mycount = `<em>${rowCount} row${rowCount == 1 ? '' : 's'} returned from</em>`;
      let caption = document.createElement('caption');
      caption.innerHTML = `${mycount} <code style="white-space: pre-wrap">${sql}</code>`;
      table.prepend(caption);
    }
  } catch ({ name, message }) {
    console.log(name, message);
    if (!SR) return;
    SR.innerHTML = '';
    SR.style.border = 'thick solid red';
    SR.style.padding = '1em';
    SR.innerHTML = `<p>${message}</p>`;
  }
}

function toggleWider(target, trigger) {
  //var questionView = document.getElementById('question-0').parentNode;
  var questionView = document.querySelector('main div.question-container').parentNode;
  if (target.className === 'container') {
    target.className = 'container-fluid';
    questionView.classList.replace('col-lg-9', 'col-lg-12');
  } else {
    target.className = 'container';
    questionView.classList.replace('col-lg-12', 'col-lg-9');
  }
}

function is_pk(idx, row, cols) {
  return (
    (cols[idx] == 'name' && row[cols.indexOf('__pk')] != 0) ||
    (cols[idx] == 'name' && row[cols.indexOf('type')].includes('PRIMARY_KEY'))
  );
}

function simulateClick(id) {
  const clickEvent = new Event('click');
  document.getElementById(id).dispatchEvent(clickEvent);
}
