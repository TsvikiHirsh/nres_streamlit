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
            xs += CrossSection.from_material(
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
    # Explanation toggle button
    if 'show_instructions' not in st.session_state:
        st.session_state.show_instructions = False

    if st.button("How to use?", key="show_instructions_button", use_container_width=True):
        st.session_state.show_instructions = not st.session_state.show_instructions

    if st.session_state.show_instructions:
        st.markdown("""
        ## Welcome to the Cross Section Plotting App!

        This app allows you to visualize cross-section data for various materials, elements, or isotopes. Here's how it works:

        ### **How to Use the App:**
        
        1. **Choose Material Type**: First, you need to select the type of material you want to plot:
            - **Materials**: Predefined materials.
            - **Elements**: Select individual elements.
            - **Isotopes**: Select isotopes based on materials or elements.
        
        2. **Select a Material**: From the available list, choose the material you want to plot. The options will change based on the material type you select.

        3. **Short Name** (Optional): You can give each material a short name to make the graph labels more readable.

        4. **Adjust Weight**: Specify the **Total Weight** for each material or component. This will influence the resulting plot. Adjust the weight using the input field.

        5. **Plot the Graph**: Once you've added all the materials, hit the **Plot Cross Sections** button to see your results.

        ### **Plot Settings:**
        - **Energy Range**: You can adjust the energy range for the plot (minimum and maximum).
        - **Scale**: Choose whether you want the X and Y axes to have a **linear** or **log** scale.
        
        Once you've configured your materials and plot settings, press **Plot Cross Sections** to visualize the data!

        ### **Important Tips:**
        - You can add multiple materials and components, and the app will automatically update the plot.
        - Use the **Remove** button to delete any unnecessary components.
        - The short names you provide will be used in the plot for better clarity.

        We hope you find this tool useful for visualizing cross-section data!
        """)

    st.title("Cross Section Plotting App")

    # Sidebar
    with st.sidebar:
        st.header("Material Selection")

        # Refresh button in the top right
        if st.button("Reset All", key="reset_button", help="Click to clear all selections and start over"):
            st.session_state.components = [{
                'id': 0,
                'material': None,
                'type': 'materials',
                'total_weight': 1.0,
                'short_name': '',
                'split_by': 'elements'
            }]
            st.session_state.next_id = 1
            st.session_state.show_instructions = False
            st.experimental_rerun()

        # Step-by-step material selection
        for idx, component in enumerate(st.session_state.components):
            # Step-by-step process - show only the current step
            with st.expander(f"Material {idx + 1} - {component['short_name'] or 'Select Material'}", expanded=True):
                # Step 1: Select Type
                if 'type_selected' not in component:
                    component['type'] = st.radio(
                        "Select type",
                        ['materials', 'elements', 'isotopes'],
                        key=f"type_{component['id']}"
                    )
                    component['type_selected'] = True

                # Step 2: Select Material based on type
                if 'material_selected' not in component:
                    material_dict = getattr(nres, component['type'])
                    component['material'] = st.selectbox(
                        "Select material",
                        options=list(material_dict.keys()),
                        key=f"material_{component['id']}"
                    )
                    component['material_selected'] = True

                # Step 3: Short Name (optional)
                if 'short_name_selected' not in component:
                    component['short_name'] = st.text_input(
                        "Short name (optional)",
                        value=component['short_name'],
                        key=f"shortname_{component['id']}"
                    )
                    component['short_name_selected'] = True

                # Step 4: Split by
                if 'splitby_selected' not in component:
                    component['split_by'] = st.selectbox(
                        "Split by",
                        options=['materials', 'elements', 'isotopes'],
                        key=f"splitby_{component['id']}"
                    )
                    component['splitby_selected'] = True

                # Step 5: Total weight
                if 'total_weight_selected' not in component:
                    component['total_weight'] = st.number_input(
                        "Total weight",
                        value=component['total_weight'],
                        min_value=0.0,
                        step=0.1,
                        key=f"weight_{component['id']}"
                    )
                    component['total_weight_selected'] = True

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

        # Plot settings
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
