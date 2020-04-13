#This task has the goal of representing the generic workflow for ANY feature template.
#This task is not intended to be run directly in a playbook as standalone task. It is supposed to be included from a parent task.
#Examples of parent tasks are the ones specific for a type of feature template, e.g. banner.
#Once a parent tasks includes this generic task some variables have to be passed, e.g. loop_over,folder and template.
#
#template_list: list of templates to be manipulated
#folder: where to store the json file of the rendered template
#template: jinja template to be used to render the final template
#
#At high level this tasks first removes all the previously rendered templates from the filesystem, then it renders the
#new ones and saves them in $folder. The tasks renders only the template with state present. We then load from
#filesystem the templates that we have just rendered, this is due to the fact that the template module is not able to
#generate facts with the rendered content. On the other side this enables multi-staged actions, meaning that we can perform
#the rendering and the upload at different phases. Once we have loaded the files we then pass them as input to the ansible module
#using the aggregate parameter for bulk operations.
#
#There are also tasks that create a list of templates with the state absent. We finally pass this list to the ansible module.
