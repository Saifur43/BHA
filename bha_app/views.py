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
import base64

import svgwrite
from django.core.files.base import ContentFile
import io
from PIL import Image
import numpy as np
import base64
from PIL import Image, ImageDraw

def generate_bha_configuration_image(configuration):
    """Generate BHA configuration image using PIL"""
    # Set image dimensions
    width = 300
    height = 800
    
    # Create new image with white background
    image = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(image)
    
    # Get components and calculate total length
    components = configuration.items.all().order_by('order')
    total_length = sum(item.component.length * item.quantity for item in components)
    
    # Calculate scaling factor
    scale_factor = (height - 100) / total_length  # Preserve some margin
    
    # Standard component width
    component_width = 60
    x_center = width // 2
    
    # Draw components
    current_depth = 50  # Start 50px from top
    
    for item in components:
        component = item.component
        component_length = item.quantity * component.length
        height_pixels = int(component_length * scale_factor)
        
        if component.image:
            try:
                # Open and resize component image
                comp_img = Image.open(component.image.path)
                comp_img = comp_img.convert('RGB')
                
                # Calculate dimensions preserving aspect ratio
                comp_width = component_width
                comp_height = height_pixels
                
                # Resize image
                comp_img = comp_img.resize((comp_width, comp_height), Image.Resampling.LANCZOS)
                
                # Paste component image
                x_pos = x_center - (comp_width // 2)
                image.paste(comp_img, (x_pos, current_depth))
                
                # Draw border
                draw.rectangle(
                    [(x_pos, current_depth), 
                     (x_pos + comp_width, current_depth + comp_height)],
                    outline='black',
                    width=1
                )
                
            except Exception as e:
                # Draw placeholder rectangle if image fails
                x_pos = x_center - (component_width // 2)
                draw.rectangle(
                    [(x_pos, current_depth),
                     (x_pos + component_width, current_depth + height_pixels)],
                    outline='black',
                    fill='lightgray',
                    width=1
                )
        
        # Add length label
        label = f'{component_length}m'
        draw.text(
            (x_center + component_width//2 + 10, current_depth + height_pixels//2),
            label,
            fill='black',
            anchor='lm'
        )
        
        current_depth += height_pixels
    
    # Convert to ContentFile
    img_buffer = io.BytesIO()
    image.save(img_buffer, format='PNG')
    return ContentFile(img_buffer.getvalue(), name='bha_configuration.png')


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
                    
                    component_ids = request.POST.getlist('component_ids[]')
                    quantities = request.POST.getlist('quantities[]')
                    
                    if not component_ids:
                        form.add_error(None, "Please add at least one component")
                        return self.form_invalid(form)
                    
                    # Create items in order of addition
                    for i, (comp_id, quantity) in enumerate(zip(component_ids, quantities)):
                        if not comp_id:  # Skip empty selections
                            continue
                            
                        component = BHAComponent.objects.get(id=comp_id)
                        BHAConfigurationItem.objects.create(
                            configuration=configuration,
                            component=component,
                            quantity=int(quantity),
                            order=i
                        )
                    
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