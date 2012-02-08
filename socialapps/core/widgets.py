from django.forms import widgets
from django.forms.widgets import flatatt
from django.utils.encoding import smart_unicode
from django.utils.safestring import mark_safe
from django.utils.html import force_unicode, conditional_escape
from django.utils import simplejson
from tagging.models import Tag
import datetime

import re
from django.forms.extras.widgets import SelectDateWidget
from django.forms.widgets import Widget, Select, MultiWidget


__all__ = ['RichTextEditor','AutoCompleteTagInput','JqueryDatePicker', 'SelectTimeWidget']
time_pattern = r'(\d\d?):(\d\d)(:(\d\d))? *([aApP]\.?[mM]\.?)?$'
RE_TIME = re.compile(time_pattern)
HOURS = 0
MINUTES = 1
SECONDS = 3
MERIDIEM = 4

class RichTextEditor(widgets.Textarea):
    editor_settings = dict ()

    def update_settings(self,custom):
        return_dict = self.editor_settings.copy()
        return_dict = update(custom)
        return return_dict

    def render(self, name, value, attrs=None):
        if value is None: value = ''
        value = smart_unicode(value)
        final_attrs = self.build_attrs(attrs, name=name)

        return mark_safe(u'''
        <textarea%s>%s</textarea>
        <script type="text/javascript">
            $(document).ready(function() {
                $.cleditor.defaultOptions.controls = "bold italic underline | style | " +
                                                    "bullets numbering | outdent " +
                                                    "indent | alignleft center alignright | undo redo | " +
                                                    "table image link unlink | pastetext | source";
                $.cleditor.defaultOptions.width = 650;
                $.cleditor.defaultOptions.height = 200;
                $("textarea#%s").cleditor();
            });
        </script>''' % (flatatt(final_attrs),
                        conditional_escape(force_unicode(value)),
                        final_attrs['id'],))

class AutoCompleteTagInput(widgets.TextInput):
    def __init__(self, tagged_model, attrs=None):
        super(AutoCompleteTagInput, self).__init__(attrs)
        self.tagged_model = tagged_model

    def render(self, name, value, attrs=None):
        output = super(AutoCompleteTagInput, self).render(name, value, attrs)
        page_tags = Tag.objects.usage_for_model(self.tagged_model)
        tag_list = simplejson.dumps([tag.name for tag in page_tags],
                                    ensure_ascii=False)
        return output + mark_safe(u'''<script type="text/javascript">
            (function( $ ){
              var availableTags = %s;

              function split( val ) {
                return val.split( /,\s*/ );
              }

              function extractLast( term ) {
                return split( term ).pop();
              }

              $("#id_%s").autocomplete({
                            minLength: 0,
                            source: function( request, response ) {
                                    // delegate back to autocomplete, but extract the last term
                                    response( $.ui.autocomplete.filter(
                                            availableTags,
                                            extractLast( request.term ) ) );
                                    },
                            focus: function() {
				                   // prevent value inserted on focus
				                   return false;
                                   },
                            select: function( event, ui ) {
				                    var terms = split( this.value );
				                    // remove the current input
				                    terms.pop();
				                    // add the selected item
				                    terms.push( ui.item.value );
				                    // add placeholder to get the comma-and-space at the end
				                    terms.push( "" );
                                    this.value = terms.join( ", " );
				                    return false;
			                        }
              });

            })( jQuery );
            </script>''' % (tag_list, name))

class JqueryDatePicker(widgets.DateInput):
    format = '%d-%m-%Y'     #ISO-8601 '2006-10-25'
    jq_format ='dd/mm/yy'

    def render(self,name,value,attrs=None):
        output = super(JqueryDatePicker, self).render(name, value, attrs)
        return mark_safe(u'''
            <script type="text/javascript">
			$(function() {
                $( "#id_%s" ).datepicker({dateFormat: "%s"});
              });
            </script>
            ''' % (name, self.jq_format)) + output

class SelectTimeWidget(widgets.DateInput):
    """
    A Widget that splits time input into <select> elements.
    Allows form to show as 24hr: <hour>:<minute>:<second>, (default)
    or as 12hr: <hour>:<minute>:<second> <am|pm> 

    Also allows user-defined increments for minutes/seconds
    """
    hour_field = '%s_hour'
    minute_field = '%s_minute'
    second_field = '%s_second' 
    meridiem_field = '%s_meridiem'
    twelve_hr = False # Default to 24hr

    def __init__(self, attrs=None, hour_step=None, minute_step=None, second_step=None, twelve_hr=False):
        """
        hour_step, minute_step, second_step are optional step values for
        for the range of values for the associated select element
        twelve_hr: If True, forces the output to be in 12-hr format (rather than 24-hr)
        """
        self.attrs = attrs or {}
        
        if twelve_hr:
            self.twelve_hr = True # Do 12hr (rather than 24hr)
            self.meridiem_val = 'a.m.' # Default to Morning (A.M.)
        
        if hour_step and twelve_hr:
            self.hours = range(1,13,hour_step) 
        elif hour_step: # 24hr, with stepping.
            self.hours = range(0,24,hour_step)
        elif twelve_hr: # 12hr, no stepping
            self.hours = range(1,13)
        else: # 24hr, no stepping
            self.hours = range(0,24) 

        if minute_step:
            self.minutes = range(0,60,minute_step)
        else:
            self.minutes = range(0,60)

        if second_step:
            self.seconds = range(0,60,second_step)
        else:
            self.seconds = range(0,60)

	def render(self, name, value, attrs=None):
	        try: # try to get time values from a datetime.time object (value)
	            hour_val, minute_val, second_val = value.hour, value.minute, value.second
	            if self.twelve_hr:
	                if hour_val >= 12:
	                    self.meridiem_val = 'p.m.'
	                else:
	                    self.meridiem_val = 'a.m.'	
	        except AttributeError:
	            hour_val = minute_val = second_val = 0
	            if isinstance(value, basestring):
	                match = RE_TIME.match(value)
	                if match:
	                    time_groups = match.groups();
	                    hour_val = int(time_groups[HOURS]) % 24 # force to range(0-24)
	                    minute_val = int(time_groups[MINUTES]) 
	                    if time_groups[SECONDS] is None:
	                        second_val = 0
	                    else:
	                        second_val = int(time_groups[SECONDS])

	                    # check to see if meridiem was passed in
	                    if time_groups[MERIDIEM] is not None:
	                        self.meridiem_val = time_groups[MERIDIEM]
	                    else: # otherwise, set the meridiem based on the time
	                        if self.twelve_hr:
	                            if hour_val >= 12:
	                                self.meridiem_val = 'p.m.'
	                            else:
	                                self.meridiem_val = 'a.m.'
	                        else:
	                            self.meridiem_val = None
	
			# If we're doing a 12-hr clock, there will be a meridiem value, so make sure the
	        # hours get printed correctly
	        if self.twelve_hr and self.meridiem_val:
	            if self.meridiem_val.lower().startswith('p') and hour_val > 12 and hour_val < 24:
	                hour_val = hour_val % 12
	        elif hour_val == 0:
	            hour_val = 12

	        output = []
	        if 'id' in self.attrs:
	            id_ = self.attrs['id']
	        else:
	            id_ = 'id_%s' % name
	
			# For times to get displayed correctly, the values MUST be converted to unicode
	        # When Select builds a list of options, it checks against Unicode values
	        hour_val = u"%.2d" % hour_val
	        minute_val = u"%.2d" % minute_val
	        second_val = u"%.2d" % second_val

	        hour_choices = [("%.2d"%i, "%.2d"%i) for i in self.hours]
	        local_attrs = self.build_attrs(id=self.hour_field % id_)
	        select_html = Select(choices=hour_choices).render(self.hour_field % name, hour_val, local_attrs)
	        output.append(select_html)

	        minute_choices = [("%.2d"%i, "%.2d"%i) for i in self.minutes]
	        local_attrs['id'] = self.minute_field % id_
	        select_html = Select(choices=minute_choices).render(self.minute_field % name, minute_val, local_attrs)
	        output.append(select_html)

	        second_choices = [("%.2d"%i, "%.2d"%i) for i in self.seconds]
	        local_attrs['id'] = self.second_field % id_
	        select_html = Select(choices=second_choices).render(self.second_field % name, second_val, local_attrs)
	        output.append(select_html)	
		raise NotImplementedError
	
	        if self.twelve_hr:
	            #  If we were given an initial value, make sure the correct meridiem gets selected.
	            if self.meridiem_val is not None and  self.meridiem_val.startswith('p'):
	                    meridiem_choices = [('p.m.','p.m.'), ('a.m.','a.m.')]
	            else:
	                meridiem_choices = [('a.m.','a.m.'), ('p.m.','p.m.')]

	            local_attrs['id'] = local_attrs['id'] = self.meridiem_field % id_
	            select_html = Select(choices=meridiem_choices).render(self.meridiem_field % name, self.meridiem_val, local_attrs)
	            output.append(select_html)

	        return mark_safe(u'\n'.join(output))

	def id_for_label(self, id_):
	    return '%s_hour' % id_
	id_for_label = classmethod(id_for_label)

    def value_from_datadict(self, data, files, name):
        # if there's not h:m:s data, assume zero:
        h = data.get(self.hour_field % name, 0) # hour
        m = data.get(self.minute_field % name, 0) # minute 
        s = data.get(self.second_field % name, 0) # second

        meridiem = data.get(self.meridiem_field % name, None)

        #NOTE: if meridiem is None, assume 24-hr
        if meridiem is not None:
            if meridiem.lower().startswith('p') and int(h) != 12:
                h = (int(h)+12)%24 
            elif meridiem.lower().startswith('a') and int(h) == 12:
                h = 0

        if (int(h) == 0 or h) and m and s:
            return '%s:%s:%s' % (h, m, s)

        return data.get(name, None)	

