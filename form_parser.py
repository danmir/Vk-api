from html.parser import HTMLParser


class FormParser(HTMLParser):

    '''
    Parse html forms
    '''

    def __init__(self):
        HTMLParser.__init__(self)
        # Form url
        self.url = None
        # Form params needs to be filled
        self.params = {}
        # In Form state between <form></form>
        self.in_form = False
        # Form already parsed
        self.form_parsed = False
        # Form method
        self.method = "GET"

    def handle_starttag(self, tag, attrs):
        tag = tag.lower()

        if tag == "form":
            if self.form_parsed:
                raise RuntimeError("Second form on page")
            if self.in_form:
                raise RuntimeError("Already in form")
            self.in_form = True

        if not self.in_form:
            # Not in form yet
            # Don't need to parse any tags
            # when not in form
            return

        # Get attributes
        attrs = dict((name.lower(), value) for name, value in attrs)

        if tag == "form":
            # Save form url
            self.url = attrs["action"]
            # Get form method, for processing http request
            if "method" in attrs:
                self.method = attrs["method"]
        # Get only proper params
        elif tag == "input" and "type" in attrs and "name" in attrs:
            if attrs["type"] in ["hidden", "text", "password"]:
                self.params[attrs["name"]] = attrs[
                    "value"] if "value" in attrs else ""

    def handle_endtag(self, tag):
        tag = tag.lower()
        if tag == "form":
            if not self.in_form:
                raise RuntimeError("Unexpected end of <form>")
            self.in_form = False
            self.form_parsed = True
