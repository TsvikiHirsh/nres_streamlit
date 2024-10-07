import streamlit as st
import nres
import pandas as pd
from nres.cross_section import CrossSection

# Initialize session state for components if it doesn't exist
if 'components' not in st.session_state:
    st.session_state.components = [{
        'id': 0,
        'material': None,
        'type': 'materials',
        'total_weight': 1.0,
        'short_name': '',
        'split_by': 'elements'
    }]
if 'next_id' not in st.session_state:
    st.session_state.next_id = 1

# Helper function to plot cross sections
def plot_cross_section(components, emin, emax, scalex, scaley):
    xs = CrossSection()
    for component in components:
        if component['material']:  # Only process if material is selected
            material_dict = getattr(nres, component['type'])
            material = material_dict[component['material']]
            total_weight = component['total_weight']
            short_name = component['short_name'] or component['material']  # Use short_name or material name
            split_by = component['split_by']
            xs+= CrossSection.from_material(
                material,
                total_weight=total_weight,
                short_name=short_name,
                splitby=split_by
            )
    
    if xs:  # Only create plot if there are valid components
        
        # Apply the energy limits (emin, emax) to the plot
        fig = xs.iplot(emin=emin, emax=emax, scalex=scalex, scaley=scaley)
        
        st.plotly_chart(fig, use_container_width=True)

        st.table(xs.weights.to_frame("weights"))
    else:
        st.warning("Please select at least one material to plot.")

def add_component():
    st.session_state.components.append({
        'id': st.session_state.next_id,
        'material': None,
        'type': 'materials',
        'total_weight': 1.0,
        'short_name': '',
        'split_by': 'elements'
    })
    st.session_state.next_id += 1

def remove_component(component_id):
    st.session_state.components = [comp for comp in st.session_state.components 
                                 if comp['id'] != component_id]

def main():
    st.title("Cross Section Plotting App")
    
    # Sidebar
    with st.sidebar:
        st.header("Material Selection")
        
        # Create an accordion for each component
        for idx, component in enumerate(st.session_state.components):
            # Dynamic expander name based on short name or material name
            short_name = component['short_name'] or component['material']
            with st.expander(short_name if short_name else f"Material {idx + 1}", expanded=False):
                # Type selection
                component['type'] = st.radio(
                    "Select type",
                    ['materials', 'elements', 'isotopes'],
                    key=f"type_{component['id']}"
                )
                
                # Material selection
                material_dict = getattr(nres, component['type'])
                component['material'] = st.selectbox(
                    "Select material",
                    options=list(material_dict.keys()),
                    key=f"material_{component['id']}"
                )
                
                # Optional fields
                component['short_name'] = st.text_input(
                    "Short name (optional)",
                    value=component['short_name'],
                    key=f"shortname_{component['id']}"
                )
                
                component['split_by'] = st.selectbox(
                    "Split by",
                    options=['materials', 'elements', 'isotopes'],
                    key=f"splitby_{component['id']}"
                )
                
                component['total_weight'] = st.number_input(
                    "Total weight",
                    value=component['total_weight'],
                    min_value=0.0,
                    key=f"weight_{component['id']}"
                )
                
                # Remove button
                if len(st.session_state.components) > 1:
                    if st.button("Remove", key=f"remove_{component['id']}"):
                        remove_component(component['id'])
                        st.rerun()

        # Add material button
        if st.button("+ Add Material"):
            add_component()
            st.rerun()
        
        st.write("---")  # Add a divider for better separation
        # Highlighted Plot button
        if st.button("Plot Cross Sections", key="plot_button", help="Click to plot the cross sections."):
            st.session_state.plot = True
        st.write("---")  # Add a divider for better separation

        # New Sidebar Inputs for emin, emax, x-scale, and y-scale inside an expander
        with st.expander("Plot Settings", expanded=False):
            emin = st.number_input("Minimum energy (eV)", value=0.1, min_value=0.0)
            emax = st.number_input("Maximum energy (eV)", value=1e6, min_value=0.1)
            scalex = st.selectbox("X-axis scale", options=["linear", "log"], index=1)
            scaley = st.selectbox("Y-axis scale", options=["linear", "log"], index=1)


    
    # Main area
    if 'plot' in st.session_state and st.session_state.plot:
        plot_cross_section(st.session_state.components, emin, emax, scalex, scaley)
        st.session_state.plot = False


if __name__ == "__main__":
    main()
