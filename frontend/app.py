"""
Exercise 02 — Streamlit Dashboard

Implement a Streamlit frontend that consumes the Node Registry API.

The dashboard must:
- Display a table of all registered nodes (GET /api/nodes from the API)
- Show a form to register a new node (POST /api/nodes)
- Allow deleting a node by name (DELETE /api/nodes/{name})
- Show a health status indicator (GET /health)

The API runs at the URL in the API_URL environment variable (default: http://api:8080).
"""

# TODO: Implement your Streamlit dashboard here


import streamlit as st
import requests
import os
from datetime import datetime
from typing import Optional

# Configuration
API_URL = os.getenv("API_URL", "http://api:8080")
st.set_page_config(
    page_title="Node Registry Dashboard",
    page_icon="🖥️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Session state initialization
if "refresh_key" not in st.session_state:
    st.session_state.refresh_key = 0

# Custom CSS for better styling
st.markdown("""
    <style>
    .stTabs [data-baseweb="tab-list"] button {
        font-size: 18px;
        font-weight: 600;
    }
    .node-card {
        padding: 20px;
        border-radius: 10px;
        background-color: #f8f9fa;
        border: 1px solid #e9ecef;
        margin-bottom: 15px;
    }
    .success-box {
        padding: 15px;
        border-radius: 5px;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
    }
    .error-box {
        padding: 15px;
        border-radius: 5px;
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
    }
    </style>
    """, unsafe_allow_html=True)

# Header
st.title("🖥️ Node Registry Dashboard")
st.markdown("*Manage your distributed system nodes efficiently*")

def get_api_headers():
    """Return headers for API requests."""
    return {"Content-Type": "application/json"}

def get_all_nodes():
    """Fetch all nodes from the API."""
    try:
        response = requests.get(f"{API_URL}/api/nodes", headers=get_api_headers(), timeout=5)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error connecting to API: {str(e)}")
        return []

def get_node_by_name(name: str):
    """Fetch a specific node by name."""
    try:
        response = requests.get(f"{API_URL}/api/nodes/{name}", headers=get_api_headers(), timeout=5)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            return None
        st.error(f"Error fetching node: {e.response.json().get('detail', str(e))}")
        return None
    except requests.exceptions.RequestException as e:
        st.error(f"Error connecting to API: {str(e)}")
        return None

def create_node(name: str, host: str, port: int):
    """Create a new node."""
    try:
        payload = {"name": name, "host": host, "port": port}
        response = requests.post(
            f"{API_URL}/api/nodes",
            json=payload,
            headers=get_api_headers(),
            timeout=5
        )
        response.raise_for_status()
        return True, "Node registered successfully!"
    except requests.exceptions.HTTPError as e:
        error_detail = e.response.json().get('detail', str(e))
        return False, f"{error_detail}"
    except requests.exceptions.RequestException as e:
        return False, f"Error connecting to API: {str(e)}"

def update_node(name: str, new_host: Optional[str] = None, new_port: Optional[int] = None):
    """Update a node's host and/or port."""
    try:
        payload = {}
        if new_host:
            payload["host"] = new_host
        if new_port:
            payload["port"] = new_port
        
        if not payload:
            return False, "At least one field (host or port) must be provided"
        
        response = requests.put(
            f"{API_URL}/api/nodes/{name}",
            json=payload,
            headers=get_api_headers(),
            timeout=5
        )
        response.raise_for_status()
        return True, "Node updated successfully!"
    except requests.exceptions.HTTPError as e:
        error_detail = e.response.json().get('detail', str(e))
        return False, f"{error_detail}"
    except requests.exceptions.RequestException as e:
        return False, f"Error connecting to API: {str(e)}"

def delete_node(name: str):
    """Delete a node."""
    try:
        response = requests.delete(
            f"{API_URL}/api/nodes/{name}",
            headers=get_api_headers(),
            timeout=5
        )
        response.raise_for_status()
        return True, "Node deleted successfully!"
    except requests.exceptions.HTTPError as e:
        error_detail = e.response.json().get('detail', str(e))
        return False, f"{error_detail}"
    except requests.exceptions.RequestException as e:
        return False, f"Error connecting to API: {str(e)}"

# Main tabs
tab1, tab2, tab3 = st.tabs(["📝 Register Node", "📊 View All Nodes", "🔍 Search"])

# ==================== TAB 1: REGISTER NODE ====================
with tab1:
    st.header("Register New Node")
    st.markdown("---")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### Node Information")
        
        node_name = st.text_input(
            "Node Name *",
            placeholder="e.g., node-01",
            help="Unique identifier for the node"
        )
        
        col_host, col_port = st.columns(2)
        with col_host:
            node_host = st.text_input(
                "Host Address *",
                placeholder="e.g., 192.168.1.10",
                help="IP address or hostname"
            )
        
        with col_port:
            node_port = st.number_input(
                "Port *",
                min_value=1,
                max_value=65535,
                value=8080,
                help="Port number (1-65535)"
            )
        
        st.markdown("---")
        
        # Validate form
        is_valid = (
            node_name.strip() != "" 
            and node_host.strip() != "" 
            and 1 <= node_port <= 65535
        )
        
        # Form submission
        if st.button("🚀 Register Node", use_container_width=True, type="primary", disabled=not is_valid):
            # Validation
            if not node_name.strip():
                st.toast("Node name is required", icon="❌")
            elif not node_host.strip():
                st.toast("Host address is required", icon="❌")
            elif node_port < 1 or node_port > 65535:
                st.toast("Port must be between 1 and 65535", icon="❌")
            else:
                success, message = create_node(node_name.strip(), node_host.strip(), node_port)
                if success:
                    st.toast(message, icon="✅")
                    st.session_state.refresh_key += 1
                    st.rerun()
                else:
                    st.toast(message, icon="❌")
    
    with col2:
        st.markdown("### Status")
        try:
            response = requests.get(f"{API_URL}/health", timeout=3)
            if response.status_code == 200:
                health = response.json()
                st.metric("API Status", "🟢 Online", help="API is running")
                st.metric("Database", f"✅ {health.get('db', 'N/A')}")
                st.metric("Registered Nodes", health.get('nodes_count', 0))
        except:
            st.warning("⚠️ API unreachable")

# ==================== TAB 2: VIEW ALL NODES ====================
with tab2:
    st.header("Registered Nodes")
    st.markdown("---")
    
    nodes = get_all_nodes()
    
    if not nodes:
        st.info("📭 No nodes registered yet. Go to 'Register Node' tab to create one.")
    else:
        st.markdown(f"**Total Nodes:** {len(nodes)}")
        
        for node in nodes:
            with st.container():
                col1, col2, col3, col4 = st.columns([2, 1.5, 1.5, 1])
                
                # Check if node is marked for deletion confirmation
                show_confirm = st.session_state.get(f"show_confirm_delete_{node['id']}", False)
                
                with col1:
                    st.markdown(f"### {node['name']}")
                    st.caption(f"ID: {node['id']}")
                
                with col2:
                    value_color = "green" if node['status'].lower() == "active" else "red"
                    st.markdown(f"**Host:** :{value_color}[`{node['host']}`]")
                    st.markdown(f"**Port:** :{value_color}[`{node['port']}`]")
                
                with col3:
                    st.markdown(f"**Status:** {node['status']}")
                    created = datetime.fromisoformat(node['created_at']).strftime("%Y-%m-%d %H:%M")
                    st.caption(f"Created: {created}")
                
                with col4:
                    col_edit, col_delete = st.columns(2)
                    with col_edit:
                        if st.button("✏️ Edit", key=f"edit_{node['id']}", use_container_width=True, disabled=show_confirm):
                            st.session_state[f"edit_mode_{node['id']}"] = not st.session_state.get(f"edit_mode_{node['id']}", False)
                            st.rerun()
                    
                    with col_delete:
                        if st.button("🗑️ Delete", key=f"delete_{node['id']}", use_container_width=True, disabled=show_confirm):
                            st.session_state[f"show_confirm_delete_{node['id']}"] = True
                            st.rerun()
                
                # Edit mode
                if st.session_state.get(f"edit_mode_{node['id']}", False):
                    st.markdown("---")
                    st.markdown("#### Edit Node")
                    
                    col_host, col_port = st.columns(2)
                    with col_host:
                        new_host = st.text_input(
                            "New Host (optional)",
                            value=node['host'],
                            key=f"host_{node['id']}",
                            help="Leave empty to keep current value"
                        )
                    
                    with col_port:
                        new_port = st.number_input(
                            "New Port (optional)",
                            min_value=1,
                            max_value=65535,
                            value=node['port'],
                            key=f"port_{node['id']}",
                            help="Leave unchanged to keep current value"
                        )
                    
                    col_save, col_cancel = st.columns(2)
                    with col_save:
                        if st.button("💾 Save Changes", key=f"save_{node['id']}", use_container_width=True):
                            host_changed = new_host.strip() != node['host']
                            port_changed = new_port != node['port']
                            
                            if not host_changed and not port_changed:
                                st.toast("No changes made", icon="⚠️")
                            else:
                                success, message = update_node(
                                    node['name'],
                                    new_host.strip() if host_changed else None,
                                    new_port if port_changed else None
                                )
                                if success:
                                    st.toast(message, icon="✅")
                                    st.session_state[f"edit_mode_{node['id']}"] = False
                                    st.session_state.refresh_key += 1
                                    st.rerun()
                                else:
                                    st.toast(message, icon="❌")
                    
                    with col_cancel:
                        if st.button("❌ Cancel", key=f"cancel_{node['id']}", use_container_width=True):
                            st.session_state[f"edit_mode_{node['id']}"] = False
                            st.rerun()
                
                # Delete confirmation
                if show_confirm:
                    st.warning(f"⚠️ Are you sure you want to delete **{node['name']}**? This action cannot be undone.")
                    col_confirm, col_cancel_delete = st.columns(2)
                    with col_confirm:
                        if st.button("✓ Confirm Delete", key=f"confirm_del_{node['id']}", use_container_width=True):
                            success, message = delete_node(node['name'])
                            if success:
                                st.toast(message, icon="✅")
                                st.session_state.refresh_key += 1
                                st.rerun()
                            else:
                                st.toast(message, icon="❌")
                                st.session_state[f"show_confirm_delete_{node['id']}"] = False
                                st.rerun()
                    
                    with col_cancel_delete:
                        if st.button("✗ Cancel", key=f"cancel_del_{node['id']}", use_container_width=True):
                            st.session_state[f"show_confirm_delete_{node['id']}"] = False
                            st.rerun()
                
                st.divider()

# ==================== TAB 3: SEARCH ====================
with tab3:
    st.header("Search Nodes")
    st.markdown("---")
    
    search_name = st.text_input(
        "Enter Node Name",
        placeholder="e.g., node-01",
        help="Search for a specific node by its name"
    )
    
    if st.button("🔎 Search", use_container_width=False, type="primary"):
        if not search_name.strip():
            st.toast("Please enter a node name to search", icon="⚠️")
        else:
            node = get_node_by_name(search_name.strip())
            
            if node is None:
                st.toast(f"Node '{search_name}' not found", icon="❌")
                st.session_state["last_searched_node"] = None
            else:
                st.session_state["last_searched_node"] = node
                st.toast(f"Node found!", icon="✅")
    
    # Display search results persistently
    if "last_searched_node" in st.session_state and st.session_state["last_searched_node"]:
        node = st.session_state["last_searched_node"]
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Node Name", node['name'])
            st.metric("Status", node['status'])
        
        with col2:
            st.metric("Host", f"`{node['host']}`")
            st.metric("Port", node['port'])
        
        with col3:
            created = datetime.fromisoformat(node['created_at']).strftime("%Y-%m-%d %H:%M:%S")
            updated = datetime.fromisoformat(node['updated_at']).strftime("%Y-%m-%d %H:%M:%S")
            st.markdown(f"**Created:** {created}")
            st.markdown(f"**Updated:** {updated}")
        
        st.divider()
        
        st.markdown("### Tips")
        st.info("""
        - Use the search box to find a specific node by its exact name
        - Once found, you can view all node details and edit them directly
        - Both host and port fields are optional for updates
        """) 
