import os

import chevron
import lxml.html
import prairielearn as pl


def prepare(element_html, data):

    element = lxml.html.fragment_fromstring(element_html)

    required_attribs = []
    optional_attribs = [
        "dbfile",
        "foreign_keys",
    ]

    pl.check_attribs(
        element, required_attribs=required_attribs, optional_attribs=optional_attribs
    )

    data["params"]["element-pl-sqlite"] = {
        "dbfile": pl.get_string_attrib(element, "dbfile", None),
        "queries": [],
    }

    if pl.has_attrib(element, "foreign_keys"):
        data["params"]["element-pl-sqlite"]["queries"].append(
            {
                "sql": "PRAGMA foreign_keys = ON;",
            }
        )

    for child in element.xpath(".//query | .//sandbox[@answers-name]"):
        # print(lxml.etree.tostring(child, pretty_print=True).decode())

        if child.tag == "query":
            data["params"]["element-pl-sqlite"]["queries"].append(
                {
                    "sql": child.text.strip(),
                }
            )

        if child.tag == "sandbox":
            answers_name = pl.get_string_attrib(child, "answers-name")
            pl.check_answers_names(data, answers_name)

            data["params"]["element-pl-sqlite"]["queries"].append(
                {
                    "answers_name": answers_name,
                }
            )

            answer = child.findtext("answer")
            if answer:
                data["correct_answers"][answers_name] = answer.replace(
                    "\n", " "
                ).strip()

    # pprint(data["params"]["element-pl-sqlite"])


def render(element_html, data):

    #'options': {'client_files_question_url': '/pl/course_instance/33/instructor/question/1172/clientFilesQuestion',
    # 'client_files_course_url': '/pl/course_instance/33/instructor/question/1172/clientFilesCourse',
    # 'client_files_question_dynamic_url': '/pl/course_instance/33/instructor/question/1172/generatedFilesQuestion/variant/4212',
    # 'submission_files_url': None, 'base_url': '/pl/course_instance/33/instructor',
    # 'workspace_url': None, 'question_path': '/course4/questions/davesqlite',
    # 'client_files_question_path': '/course4/questions/davesqlite/clientFilesQuestion',
    # 'client_files_course_path': '/course4/clientFilesCourse',
    # 'server_files_course_path': '/course4/serverFilesCourse', 'course_extensions_path': '/course4/elementExtensions',
    # 'client_files_element_url': '/pl/course_instance/33/instructor/elements/pl-sqlite/clientFilesElement',
    # 'client_files_extensions_url': {}}, 'raw_submitted_answers': {}, 'editable': True, 'manual_grading': False,
    # 'panel': 'question', 'num_valid_submissions': 0, 'extensions': []}

    localDev = os.path.exists("localDevelopment.txt")

    element = lxml.html.fragment_fromstring(element_html)

    for child in element.iterfind(".//sandbox"):
        preloads = []
        html_params = {
            "uuid": pl.get_uuid(),
            "editable": data.get("editable", True),
            "localDev": localDev,
        }

        answers_name = pl.get_string_attrib(child, "answers-name", None)
        if answers_name:
            html_params["submitted_answer"] = data["raw_submitted_answers"].get(
                answers_name, None
            )
            html_params["answers_name"] = answers_name
            html_params["correct_answer"] = data["correct_answers"].get(
                answers_name, None
            )

        for preload in child.iterfind("preload[@slug]"):
            slug = pl.get_string_attrib(preload, "slug")
            preloads.append({"slug": slug, "content": preload.text})

        ###

        if data["panel"] == "question":
            html_params["question"] = True

            if preloads:
                # Help mustache out for comma separated lists
                preloads[-1]["last"] = True
                html_params["preload"] = preloads

            # Sandbox functionality toggle
            if data["editable"] or data["manual_grading"]:
                html_params["sandbox"] = True

        elif data["panel"] == "submission":
            html_params["submission"] = True

            html_params["editable"] = False
            html_params["parse_error"] = data["format_errors"].get(answers_name, None)

        elif data["panel"] == "answer":
            html_params["answer"] = True

        with open("sandbox.mustache", "r", encoding="utf-8") as f:
            try:
                # sandbox = lxml.html.fragment_fromstring(chevron.render(f, html_params))
                # sandbox.tail = child.tail
                # child.getparent().replace(child, sandbox)

                sandboxtags = lxml.html.fragments_fromstring(
                    chevron.render(f, html_params)
                )

                parent = child.getparent()
                index = parent.index(child)

                parent.remove(child)
                for i, fragment in enumerate(sandboxtags):
                    parent.insert(index + i, fragment)

            except lxml.etree.ParserError:
                # Empty string so don't include anything
                child.drop_tree()

    for child in element.iterfind(".//query"):
        html_params = {
            "uuid": pl.get_uuid(),
        }

        html_params["summary"] = pl.get_string_attrib(child, "summary", "true")
        html_params["output_id"] = "queryOutput-" + html_params["uuid"]
        html_params["quiet"] = False
        html_params["heading"] = pl.get_string_attrib(child, "title", False)
        html_params["redo"] = pl.get_string_attrib(child, "redo", False)
        html_params["deferred"] = pl.get_string_attrib(child, "deferred", False)

        if pl.has_attrib(child, "quiet"):
            html_params["quiet"] = True
            html_params["summary"] = "false"

        if pl.get_string_attrib(child, "width", None):
            html_params["width"] = pl.get_string_attrib(child, "width")

        if child.text:
            html_params["query"] = child.text.strip()
        else:
            html_params["query"] = ""

        if data["panel"] == "question":
            html_params["question"] = True
        elif data["panel"] == "submission":
            html_params["submission"] = True
        elif data["panel"] == "answer":
            html_params["answer"] = True

        with open("query.mustache", "r", encoding="utf-8") as f:
            try:
                querytags = lxml.html.fragments_fromstring(
                    chevron.render(f, html_params)
                )

                parent = child.getparent()
                index = parent.index(child)
                parent.remove(child)

                for i, fragment in enumerate(querytags):
                    parent.insert(index + i, fragment)

            except lxml.etree.ParserError:
                # Empty string don't include anything
                child.drop_tree()

    # Initialize the DB
    if data["panel"] == "question":
        with open("pl-sqlite.mustache", "r", encoding="utf-8") as f:

            html_params = {}

            # Check in question then course
            dbfile = pl.get_string_attrib(element, "dbfile", None)
            if dbfile:
                # TODO: Make this configurable, question or course
                html_params["dburl"] = (
                    data["options"]["client_files_course_url"] + "/" + dbfile
                )

            if pl.has_attrib(element, "foreign_keys"):
                html_params["foreign_keys"] = True

            # Single tag so fragment_fromtstring works
            initialize = lxml.html.fragment_fromstring(
                chevron.render(f, html_params).strip()
            )
            # index 0 just after the root
            element.insert(0, initialize)

            # Nothing here for submission or answer panels

    return pl.inner_html(element)


def parse(element_html, data):
    element = lxml.html.fragment_fromstring(element_html)

    for child in element.iterfind(".//sandbox[@answers-name]"):
        answers_name = pl.get_string_attrib(child, "answers-name")
        answer = data["submitted_answers"].get(answers_name, None)

        if not answer or not answer.strip():
            data["format_errors"][answers_name] = "No answer was submitted."
