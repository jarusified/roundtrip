import os

from IPython.core import magic_arguments
from IPython.core.magics import ExecutionMagics
from IPython.core.magic import Magics, magics_class, cell_magic, line_magic
from IPython.display import HTML, Javascript, Markdown, display, clear_output

class Render:
    def __init__(self, js="", html="", data=None):
        self.js = js
        self.html = html
        self.data = data

    def start():
        # Set up the object to map inout files to what javascript expects
        argList = '<script> var argList = []; var elementTop = null; var cell_idx = -1</script>'
        displayObj = display(HTML(argList), display_id=True)
        for i in range(2, len(args), 1):
            if("%" in args[i]):
                args[i] = self.shell.user_ns[args[i][1:]]
            if(isinstance(args[i], str) and "." in args[i]):
                if("." in args[i] and args[i].split(".")[1] in self.inputType.keys()):
                    displayObj.update(HTML("<script src=" + args[i] + " type=" + self.inputType[args[i].split(".")[1]] +"></script>"))
                if(args[i].split(".")[1] == "html" or args[i].split(".")[1] == "css"):
                    fileVal = open(args[i]).read()
                    display(HTML(fileVal))
            if(isinstance(args[i], str) and "\"" in args[i]):
                args[i] = args[i].replace("\"", "\\\"")
            if(isinstance(args[i], str) and "\n" in args[i]):
                args[i] = args[i].replace("\n", "\\n")
            displayObj.update(Javascript('argList.push("' + str(args[i]) + '")')) 

        # Get curent cell id
        self.codeMap[name] = self.js
        preRun = """
                // Grab current context
                elementTop = element.get(0);
                """
        displayObj.update(Javascript(preRun))
   
        header = """
                  <div id=\""""+name+"""\"></div>
                  <script>
                  elementTop.appendChild(document.getElementById('"""+str(name)+"""'));
                  element = document.getElementById('"""+str(name)+"""');  
                """
        footer = """</script>"""
        display(HTML(header + javascriptFile + footer))

    def __enter__(self):
        return self.start()

    def __exit__(self):
        return

    def __call__(self, func):
        """Decorate a function to provide the same behavior as with statement."""
        @wraps(func)
        def _inner(*args, **kwargs):
            self.start()
            try:
                retval = func(*args, **kwargs)
                self.end(None, None, None)
            except:
                err, err_cls, tb = sys.exc_info()
                # get the traceback excluding this
                # frame containing `_inner`
                self.end(err, err_cls, tb.tb_next)
        return _inner


@magics_class
class RoundTrip(ExecutionMagics):
    '''
    Interface that links the javascript and HTML files to render on Jupyter notebook.
    '''

    inputType = {
        "js": "text/javascript",
        "csv": "text/csv",
        "html": "text/html",
        "json": "text/json",
        "css": "text/css"
    }
     
    # Note to self: Custom magic classes MUST call parent's constructor
    def __init__(self, shell):
        """
        Reference
        """
        super().__init__(shell)

        requireInfo = RoundTrip.read_file('roundtrip/require.config')
        display(Javascript("require.config({ \
                                            baseUrl: './', \
                                            paths: { "+requireInfo+"} });"))
        # Clean up namespace function
        display(HTML("<script>function cleanUp() { argList =[]; element = null; cell_idx = -1}</script>"))
        
        # TODO: Find a better name. 
        self.codeMap = {}
    
    @cell_magic
    @magic_arguments.magic_arguments()
    @magic_arguments.argument("js", type=str)
    @magic_arguments.argument("html", type=str)
    @magic_arguments.argument("data", type=str)
    def roundtrip(self, line='', cell=None):
        """
        """
        # Get command line args for loading the vis
        args = magic_arguments.parse_argstring(self.roundtrip, line)
        
        # Read the data from each file.
        js = RoundTrip.read_file(args.js)
        data = RoundTrip.read_file(args.data)
        html = RoundTrip.read_file(args.html)

        print(js, data, html)

        with Render(js=js, html=html, data=data):
            self.shell.ex(cell)

    @staticmethod
    def read_file(filePath):
        absPath = os.path.abspath(filePath)

        with open(absPath, 'r') as f:
            data = f.read()
            return data
    
    @line_magic
    def fetchData(self, line):
        args = line[1:-1].split()
        location = args[0][:-1]
        dest = args[1][:-1]
        source = args[2]
        hook = """
                var holder = """+str(source)+""";
                holder = '"' + holder + '"';
                //console.log(holder);
                IPython.notebook.kernel.execute('"""+str(dest)+""" = '+ holder);
                //console.log('"""+str(dest)+""" = '+ holder);
               """
        display(Javascript(hook))
