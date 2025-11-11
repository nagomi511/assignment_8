from django import forms

class DHCPRequestForm(forms.Form):
    DHCP_CHOICES = [
        ('DHCPv4', 'DHCPv4'),
        ('DHCPv6', 'DHCPv6'),
    ]
    
    mac_address = forms.CharField(
        max_length=17,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '00:1A:2B:3C:4D:5E',
            'pattern': '[0-9A-Fa-f]{2}(:[0-9A-Fa-f]{2}){5}'
        }),
        help_text='Format: XX:XX:XX:XX:XX:XX'
    )
    
    dhcp_version = forms.ChoiceField(
        choices=DHCP_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
