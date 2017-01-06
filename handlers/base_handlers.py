
from google.appengine.api import users
import webapp2

import main
import utils


# Potentially helpful (or not) superclass for *logged in* pages and actions (assumes app.yaml gaurds for login)
### Pages ###
class BasePage(webapp2.RequestHandler):
  def get(self):
        user = users.get_current_user()
        template = self.get_template()
        if user:
            email = user.email().lower()
            values = {"user_email": email, "logout_url": users.create_logout_url('/login')}
            self.update_values(values)
        else:
            self.redirect('/login')
            return
        self.response.out.write(template.render(values))


  def update_values(self, email, account_info, values):
    # Subclasses should override this method to add additional data for the Jinja template.
    pass


  def get_template(self):
    # Subclasses must override this method to set the Jinja template.
    raise Exception("Subclass must implement handle_post!")
