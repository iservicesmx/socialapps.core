from django import forms
from haystack.forms import SearchForm
from .utils import has_permission

class CustomSearchForm(SearchForm):
    
    def search(self, **kwargs):
        if not self.is_valid():
            return self.no_query_found()

        if not self.cleaned_data.get('q'):
            return self.no_query_found()

        user = kwargs.get('user', None)

        sqs = self.searchqueryset.auto_query(self.cleaned_data['q'])
        
        if user:
            ids = []
            for item in sqs:
                if not item.object.site == user.person.site:
                    ids.append('%s.%s.%s' % (item.app_label, item.model_name, item.pk))
                if item.model_name == 'basecontent':
                    if not has_permission(item.object.get_type_object(), user, 'socialize'):
                        ids.append('cms.basecontent.%s' % item.pk)
            sqs = sqs.exclude(id__in=ids)
        
        if self.load_all:
            sqs = sqs.load_all()
        
        return sqs
