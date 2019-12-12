from django import forms

class LocationForm(forms.Form):
	autocomplete = forms.CharField(label="autofill",
						    max_length=50,
							widget=forms.TextInput(attrs={'id': 'autocomplete',
													   'class': 'form-control',
													   'placeholder':'Search Address',
													   'type':'text',
													   'autofocus': 'True',
								  					   'onFocus':'geolocate()'}))	

	street_number = forms.IntegerField(label="street number",
						    widget=forms.TextInput(attrs={'id': 'street_number',
						    						   'class': 'form-control',
													   'placeholder':'#',
					  							 	   'readonly': 'readonly',
					  							  	   'name': 'street_number',
   													   'type':'text'}))
	route = forms.CharField(label="street name",
							max_length=50,
							widget=forms.TextInput(attrs={'id': 'route',
													   'class': 'form-control',
													   'placeholder':'Street',
						  							   'readonly': 'readonly',
						  							   'name': 'route',
   													   'type':'text'}))

	locality = forms.CharField(label="locality",
						    max_length=50,
							widget=forms.TextInput(attrs={'id': 'locality',
													   'class': 'form-control',
													   'placeholder':'City/Town',
								  					   'readonly': 'readonly',
								  					   'name': 'locality',
   													   'type':'text'}))

	administrative_area_level_1 = forms.CharField(label="administrative_area_level_1",
						    max_length=50,
							widget=forms.TextInput(attrs={'id': 'administrative_area_level_1',
													   'class': 'form-control',
													   'placeholder':'State',
								  					   'readonly': 'readonly',
								  					   'name': 'administrative_area_level_1',
   													   'type':'text'}))

	country = forms.CharField(label="country",
						    max_length=50,
							widget=forms.TextInput(attrs={'id': 'country',
									  	 			   'class': 'form-control',
													   'placeholder':'Country',
								  					   'readonly': 'readonly',
								  					   'name': 'country',
   													   'type':'text'}))

	postal_code = forms.CharField(label="postal_code",
						    max_length=50,
							widget=forms.TextInput(attrs={'id': 'postal_code',
													   'class': 'form-control',
													   'placeholder':'Zipcode',
								  					   'readonly': 'readonly',
								  					   'name': 'postal_code',
   													   'type':'text'}))
def clean(self):
    cleaned_data = super(LocationForm, self).clean()
    autocomplete = cleaned_data.get('autocomplete')
    street_number = cleaned_data.get('street_number')
    route = cleaned_data.get('route')
    locality = cleaned_data.get('locality')
    administrative_area_level_1 = cleaned_data.get('administrative_area_level_1')
    country = cleaned_data.get('country')
    postal_code = cleaned.data.get('postal_code')
    if not autocomplete and not street_number and not route and not locality and not administrative_area_level_1 and not country and not postal_code:
        raise forms.ValidationError('You have to write something!')