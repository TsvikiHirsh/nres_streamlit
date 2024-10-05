import nres.cross_section
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import nres

# Load the available options from nres dicts
MATERIALS = nres.materials # Update based on the actual nres nres.materials
ELEMENTS = nres.elements
ISOTOPES = nres.isotopes

# Helper function to plot cross sections
def plot_cross_section(components):
    
    xs = {}
    for component in components:
        material = nres.materials[component['material']]
        # st.write(material)
        total_weight = component['total_weight']
        short_name = component['short_name']
        split_by = component['split_by']

        xs[nres.CrossSection.from_material(material,total_weight=total_weight,short_name=short_name,splitby=split_by)] = total_weight
        
    
    # Plot the cross section for each component
    xs = nres.CrossSection(xs)
    fig = xs.iplot()
    
    st.plotly_chart(fig, use_container_width=True)

# Streamlit app layout
st.title("Cross Section Plotting App")
st.write("Select materials, elements, or isotopes and combine them for cross-section plotting.")

# Define number of components (for user flexibility)
num_components = st.number_input("Number of Components", min_value=1, max_value=10, value=1)

components = []

for i in range(num_components):
    st.subheader(f"Component {i + 1}")

    # Choose between material, element, or isotope
    component_type = st.selectbox(f"Select Type for Component {i + 1}", 
                                  ['Material', 'Element', 'Isotope'], key=f"type_{i}")
    
    if component_type == 'Material':
        material = st.selectbox(f"Choose Material for Component {i + 1}", list(MATERIALS.keys()), key=f"material_{i}")
    elif component_type == 'Element':
        material = st.selectbox(f"Choose Element for Component {i + 1}", list(ELEMENTS.keys()), key=f"element_{i}")
    else:
        material = st.selectbox(f"Choose Isotope for Component {i + 1}", list(ISOTOPES.keys()), key=f"isotope_{i}")
    
    total_weight = st.number_input(f"Total Weight for {component_type} {i + 1}", min_value=0.0, value=1.0, key=f"weight_{i}")
    
    short_name = st.text_input(f"Short Name for Component {i + 1}", f"{component_type}_{i + 1}", key=f"shortname_{i}")
    
    split_by = st.selectbox(f"Split by for Component {i + 1}", ['isotopes', 'elements', 'materials'], key=f"splitby_{i}")
    
    components.append({
        'material': material,
        'total_weight': total_weight,
        'short_name': short_name,
        'split_by': split_by
    })

# Plot button
if st.button("Plot Cross Section"):
    plot_cross_section(components)
