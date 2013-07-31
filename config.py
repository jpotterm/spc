import re
from urlparse import urlparse

sim_input_template = './static/mendel.in'
sim_input_file = './engine/mendel.in'
sim_out_path = './output/'
sim_exe_path = './engine'
sim_exe = 'mendel'

# for user authentication
user='wes'
password='john3.16'

# define user input parameters here and set them with default values
#params = dict(case_id='xyz123',mutn_rate=10,frac_fav_mutn=0.00001,
#              reproductive_rate=2,pop_size=100,num_generations=50)

# define parameters for executing simulation
exe = dict(path='engine/mendel')

# user must write their own function for how to write the output file
def write_params(form_params):
   '''write the input file needed for the simulation'''
   f = open(sim_input_file, 'w')
   # need to know what attributes are in what blocks
   params, blockmap, blockorder = read_namelist() 
   for block in blockorder:
       f.write("&%s\n" % block)
       for key in blockmap[block]:
           m = re.search(r'[a-zA-Z]',form_params[key])
           if m:
               if not re.search('[0-9.]*e+[0-9]*|[FT]',m.group()):
                   form_params[key] = "'" + form_params[key] + "'"
           f.write(key + ' = ' + form_params[key] + "\n")
       f.write("/\n\n")
   f.close
   return 1

def read_namelist():
    '''read the namelist file and return as a dictionary'''
    params = dict()
    blockmap = dict() 
    blockorder = []
    for line in open(sim_input_template, 'rU'):
        m = re.search(r'&(\w+)',line) # block title
        n = re.search(r'(\w+) = (.*$)',line) # parameter
        if m:
            block = m.group(1)  
            blockorder += [ m.group(1) ]
        elif n:
            # Delete apostrophes
            val = re.sub(r"'", "", n.group(2))
            # Delete Fortran comments 
            params[n.group(1)] = re.sub(r'\!.*$', "", val)
            # Append to blocks e.g. {'basic': ['case_id', 'mutn_rate']}
            blockmap.setdefault(block,[]).append(n.group(1))
    return params, blockmap, blockorder

def write_html_template():
# need to output according to blocks
    confirm="/confirm"
    f = open('out.tpl', 'w')
    params, blockmap, blockorder = read_namelist() 
    f.write("<html>\n")
    f.write("<head>\n")
    f.write("<script type=\"text/javascript\" src=\"/static/main.js\" charset=\"utf-8\"></script>\n")
    f.write("<link type=\"text/css\" rel=\"StyleSheet\" href=\"/static/default.css\" />")
    f.write("</head>\n")
    f.write("<body onload=\"init()\">\n")
    f.write("<form action=\""+confirm+"\" method=\"post\">\n")
    f.write("<input type=\"submit\" />\n")
    for block in blockorder:
        f.write("\n\n<h2>" + block + "</h2>\n")
        f.write("<table><tbody>\n")
        for param in blockmap[block]:
            str = "<tr><td>"
            str += param
            str += ":</td><td><input type=\"text\" name=\"" + param + "\" "
            str += "value=\"{{" + param + "}}\"/>"
            str += "</td></tr>\n"
            f.write(str)
        f.write("</tbody></table>\n")
    f.write("</form>\n")
    f.write("</body>\n")
    f.write("</html>\n")
    f.close()
    return 1

