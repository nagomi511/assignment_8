from django.shortcuts import render

# Create your views here.

from django.http import JsonResponse
from datetime import datetime
from .forms import DHCPRequestForm
from .dhcp_logic import assign_ip, validate_mac_address, bitwise_check_odd_even
from .db_connection import get_db_connection

def index(request):
    """Main page with DHCP request form"""
    context = {
        'form': DHCPRequestForm(),
        'result': None
    }
    
    if request.method == 'POST':
        form = DHCPRequestForm(request.POST)
        if form.is_valid():
            mac_address = form.cleaned_data['mac_address'].upper()
            dhcp_version = form.cleaned_data['dhcp_version']
            
            # Validate MAC
            if not validate_mac_address(mac_address):
                context['error'] = "Invalid MAC address format"
                context['form'] = form
                return render(request, 'network/index.html', context)
            
            # Assign IP
            assigned_ip, lease_info = assign_ip(mac_address, dhcp_version)
            
            if assigned_ip is None:
                context['error'] = lease_info
                context['form'] = form
                return render(request, 'network/index.html', context)
            
            # Bitwise check
            mac_sum_parity = bitwise_check_odd_even(mac_address)
            
            # Prepare result
            result = {
                'mac_address': mac_address,
                'dhcp_version': dhcp_version,
                'assigned_ip': assigned_ip,
                'lease_time': f"{lease_info} seconds",
                'mac_sum_parity': mac_sum_parity,
                'timestamp': datetime.now().isoformat()
            }
            
            # Save to MongoDB
            db = get_db_connection()
            if db is not None:
                try:
                    db.leases.insert_one(result.copy())
                except Exception as e:
                    result['db_error'] = f"Failed to save to database: {e}"
            
            context['result'] = result
            context['form'] = DHCPRequestForm()
    
    return render(request, 'network/index.html', context)

def view_leases(request):
    """View all DHCP leases from MongoDB"""
    db = get_db_connection()
    leases = []
    error = None
    
    if db is not None:
        try:
            # Fetch all leases, sorted by timestamp descending
            leases = list(db.leases.find().sort('timestamp', -1))
        except Exception as e:
            error = f"Failed to retrieve leases: {e}"
    else:
        error = "Unable to connect to database"
    
    context = {
        'leases': leases,
        'error': error
    }
    
    return render(request, 'network/leases.html', context)
