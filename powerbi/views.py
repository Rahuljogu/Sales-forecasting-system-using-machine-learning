from django.shortcuts import render


def dashboard(request):
    """Display the locally maintained Power BI portfolio dashboard."""
    return render(request, 'powerbi/dashboard.html')
