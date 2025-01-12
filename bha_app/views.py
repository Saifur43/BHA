from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, CreateView, DetailView
from django.db import transaction
from .models import BHAComponent, BHAConfiguration, BHAConfigurationItem
from .forms import BHAComponentForm, BHAConfigurationForm
from PIL import Image, ImageDraw, ImageFont
from django.core.files.base import ContentFile
import io
from django.urls import reverse_lazy
from django.views.generic.edit import UpdateView, DeleteView

from PIL import Image, ImageDraw, ImageFont
import io
from django.core.files.base import ContentFile

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import numpy as np


def generate_bha_configuration_image(configuration):
    """Generate BHA configuration image using matplotlib"""
    # Create figure and axes with smaller size and higher DPI
    fig, (ax1, ax2) = plt.subplots(1, 2, gridspec_kw={'width_ratios': [1, 1]}, figsize=(8, 11), dpi=150)
    fig.patch.set_facecolor('white')
    plt.subplots_adjust(left=0.15, right=0.95, top=0.95, bottom=0.05, wspace=0.2)
    
    # Get components and calculate total length
    components = configuration.items.all().order_by('order')
    total_length = sum(item.component.length * item.quantity for item in components)
    
    # Set up the main axis for BHA drawing
    ax1.set_ylim(-total_length, 0)  # Set y-axis limit to total length
    ax1.set_xlim(-0.3, 0.3)
    ax1.yaxis.set_major_locator(plt.MultipleLocator(50))
    ax1.grid(False)
    
    # Style the axis
    ax1.spines['top'].set_visible(False)
    ax1.spines['right'].set_visible(False)
    ax1.spines['bottom'].set_visible(False)
    ax1.spines['left'].set_linewidth(0.5)
    
    # Remove x-axis ticks and labels
    ax1.set_xticks([])
    
    # Draw components sequentially
    current_depth = 0
    for item in components:
        component = item.component
        component_length = component.length * item.quantity
        
        if component.image:
            try:
                img = plt.imread(component.image.path)
                img_width = 0.1
                
                ax1.imshow(img, extent=[-img_width/2, img_width/2, 
                                     -(current_depth + component_length), -current_depth],
                          aspect='auto')
            except Exception as e:
                rect = patches.Rectangle((-0.15, -(current_depth + component_length)), 
                                      0.3, component_length,
                                      facecolor='lightgray',
                                      edgecolor='black',
                                      linewidth=0.5)
                ax1.add_patch(rect)
        else:
            rect = patches.Rectangle((-0.15, -(current_depth + component_length)), 
                                  0.3, component_length,
                                  facecolor='lightgray',
                                  edgecolor='black',
                                  linewidth=0.5)
            ax1.add_patch(rect)
        
        current_depth += component_length
    
    # Set up table axis
    ax2.axis('off')
    
    # Create table data
    table_data = []
    for i, item in enumerate(components, 1):
        component = item.component
        table_data.append([
            i,
            component.name,
            item.quantity,
            f"{component.length * item.quantity:.1f}"
        ])
    
    # Add total row
    table_data.append(['', 'Total:', '', f"{total_length:.1f}"])
    
    # Create table
    table = ax2.table(
        cellText=table_data,
        colLabels=['No', 'ITEM', 'Sgls', 'Length'],
        loc='top',
        cellLoc='center',
        colWidths=[0.15, 0.45, 0.15, 0.25]
    )
    
    # Style the table
    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(1.2, 1.5)
    
    # Style header row
    for i, key in enumerate(table._cells):
        cell = table._cells[key]
        if key[0] == 0:  # Header row
            cell.set_facecolor('#e6e6e6')
            cell.set_text_props(weight='bold')
        if key[0] == len(table_data):  # Total row
            cell.set_text_props(weight='bold')
    
    # Adjust layout
    plt.tight_layout()
    
    # Save to bytes
    buffer = io.BytesIO()
    canvas = FigureCanvas(fig)
    canvas.print_png(buffer)
    plt.close(fig)
    
    return ContentFile(buffer.getvalue())


class BHAComponentListView(ListView):
    model = BHAComponent
    template_name = 'bha_app/component_list.html'
    context_object_name = 'components'

class BHAComponentCreateView(CreateView):
    model = BHAComponent
    form_class = BHAComponentForm
    template_name = 'bha_app/component_form.html'
    success_url = '/components/'

class BHAConfigurationCreateView(CreateView):
    model = BHAConfiguration
    form_class = BHAConfigurationForm
    template_name = 'bha_app/configuration_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['components'] = BHAComponent.objects.all()
        return context

    def post(self, request, *args, **kwargs):
        self.object = None
        form = self.get_form()
        
        if form.is_valid():
            try:
                with transaction.atomic():
                    configuration = form.save(commit=False)
                    configuration.save()
                    
                    selected_components = request.POST.getlist('components')
                    
                    if not selected_components:
                        form.add_error(None, "Please select at least one component")
                        return self.form_invalid(form)
                    
                    # Create items list with positions
                    items_to_create = []
                    for component_id in selected_components:
                        quantity = int(request.POST.get(f'quantity_{component_id}', 1))
                        position = float(request.POST.get(f'position_{component_id}', 0))
                        component = BHAComponent.objects.get(id=component_id)
                        
                        items_to_create.append({
                            'component': component,
                            'quantity': quantity,
                            'position': position
                        })
                    
                    # Sort items by position
                    items_to_create.sort(key=lambda x: x['position'])
                    
                    # Create items with correct order
                    max_position = 0
                    for i, item in enumerate(items_to_create):
                        BHAConfigurationItem.objects.create(
                            configuration=configuration,
                            component=item['component'],
                            quantity=item['quantity'],
                            order=i,
                            position=item['position']
                        )
                        max_position = max(max_position, 
                                        item['position'] + (item['component'].length * item['quantity']))
                    
                    configuration.total_length = max_position
                    configuration.save()
                    
                    try:
                        bha_image = generate_bha_configuration_image(configuration)
                        configuration.bha_image.save(
                            f'bha_config_{configuration.id}.png', 
                            bha_image, 
                            save=True
                        )
                    except Exception as e:
                        print(f"Error generating image: {str(e)}")
                        raise
                    
                return redirect('configuration_detail', pk=configuration.pk)
                
            except Exception as e:
                print(f"Error in configuration creation: {str(e)}")
                form.add_error(None, f"Error creating configuration: {str(e)}")
                return self.form_invalid(form)
        
        return self.form_invalid(form)

class BHAConfigurationDetailView(DetailView):
    model = BHAConfiguration
    template_name = 'bha_app/configuration_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['configuration_items'] = self.object.items.all()
        return context

class BHAComponentEditView(UpdateView):
    model = BHAComponent
    form_class = BHAComponentForm
    template_name = 'bha_app/component_form.html'
    success_url = reverse_lazy('component_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edit Component'
        context['button_text'] = 'Update'
        return context

class BHAComponentDeleteView(DeleteView):
    model = BHAComponent
    template_name = 'bha_app/component_confirm_delete.html'
    success_url = reverse_lazy('component_list')

class DashboardView(ListView):
    model = BHAConfiguration
    template_name = 'bha_app/dashboard.html'
    context_object_name = 'configurations'
    ordering = ['-created_at']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_components'] = BHAComponent.objects.count()
        context['total_configurations'] = BHAConfiguration.objects.count()
        context['recent_configurations'] = BHAConfiguration.objects.order_by('-created_at')[:5]
        return context