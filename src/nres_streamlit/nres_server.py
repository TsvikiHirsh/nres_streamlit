import streamlit as st
import nres
import pandas as pd
from nres.cross_section import CrossSection

# Initialize session state for components and other flags
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

if 'show_instructions' not in st.session_state:
    st.session_state.show_instructions = False

if 'step' not in st.session_state:
    st.session_state.step = 0  # Step 0 = Material Type, Step 1 = Material Selection, etc.

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

def toggle_instructions():
    st.session_state.show_instructions = not st.session_state.show_instructions

def next_step():
    st.session_state.step += 1

def reset_steps():
    st.session_state.step = 0

def main():
    # Toggleable explanation
    st.button("Click to Learn How to Use the App", key="show_instructions_button", on_click=toggle_instructions, use_container_width=True)

    # Show explanation
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
        """)

    st.title("Cross Section Plotting App")

    # Sidebar
    with st.sidebar:
        st.header("Material Selection")
        
        # Step-by-step navigation
        if st.session_state.step == 0:  # Material Type
            st.subheader("Step 1: Select Material Type")
            component_type = st.radio(
                "Select material type",
                ['materials', 'elements', 'isotopes'],
                key="material_type"
            )
            if component_type:
                for component in st.session_state.components:
                    component['type'] = component_type
                next_step()

        elif st.session_state.step == 1:  # Material Selection
            st.subheader("Step 2: Select Material")
            component = st.session_state.components[0]  # Assuming only 1 component for now
            material_dict = getattr(nres, component['type'])
            component['material'] = st.selectbox(
                "Select material",
                options=list(material_dict.keys()),
                key=f"material_{component['id']}"
            )
            if component['material']:
                next_step()

        elif st.session_state.step == 2:  # Short Name
            st.subheader("Step 3: Optional - Enter Short Name")
            component = st.session_state.components[0]  # Assuming only 1 component for now
            component['short_name'] = st.text_input(
                "Short name (optional)",
                value=component['short_name'],
                key=f"shortname_{component['id']}"
            )
            if st.button("Skip this step", key="skip_short_name"):
                next_step()
            elif component['short_name']:
                next_step()

        elif st.session_state.step == 3:  # Total Weight
            st.subheader("Step 4: Adjust Total Weight")
            component = st.session_state.components[0]
            component['total_weight'] = st.number_input(
                "Total weight",
                value=component['total_weight'],
                min_value=0.0,
                step=0.01,
                key=f"weight_{component['id']}"
            )
            if component['total_weight'] >= 0:
                next_step()

        elif st.session_state.step == 4:  # Split by Elements/Isotopes
            st.subheader("Step 5: Select Split Type")
            component = st.session_state.components[0]
            component['split_by'] = st.selectbox(
                "Split by",
                options=['materials', 'elements', 'isotopes'],
                key=f"splitby_{component['id']}"
            )
            if component['split_by']:
                next_step()

        elif st.session_state.step == 5:  # Plot Settings
            st.subheader("Step 6: Adjust Plot Settings")
            emin = st.number_input("Minimum energy (eV)", value=0.1, min_value=0.0)
            emax = st.number_input("Maximum energy (eV)", value=1e6, min_value=0.1)
            scalex = st.selectbox("X-axis scale", options=["linear", "log"], index=1)
            scaley = st.selectbox("Y-axis scale", options=["linear", "log"], index=1)
            if st.button("Plot Cross Sections", key="plot_button", help="Click to plot the cross sections."):
                st.session_state.plot = True
                next_step()  # Finish the process

    # Main area - Plot the cross section after all steps
    if 'plot' in st.session_state and st.session_state.plot:
        plot_cross_section(st.session_state.components, emin, emax, scalex, scaley)
        st.session_state.plot = False

if __name__ == "__main__":
    main()
