app_name = "permission_studio"
app_title = "Permission Studio"
app_publisher = "Arshad"
app_description = "Unified visual permission management dashboard for Frappe"
app_email = "arshadqureshiofc@gmail.com"
app_license = "mit"

required_apps = ["frappe"]

app_include_js = ["permission_studio.bundle.js"]
app_include_css = ["permission_studio.bundle.css"]

add_to_apps_screen = [
	{
		"name": "permission_studio",
		"logo": "/assets/permission_studio/images/logo.svg",
		"title": "Permission Studio",
		# Frappe v14+ desk uses /desk/... paths; /app/... does not strip to a Page route.
		"route": "/desk/permission-studio",
		"has_permission": "permission_studio.api.matrix.has_studio_access",
	}
]
