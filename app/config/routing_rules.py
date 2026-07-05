from types import MappingProxyType


CATEGORY_TEAM_ROUTES = MappingProxyType(
    {
        "Technical Support": "Technical Support",
        "Billing": "Finance",
        "Sales Inquiry": "Sales",
        "Feature Request": "Product Team",
        "Bug Report": "Technical Support",
        "Account Access": "Customer Success",
        "Refund Request": "Finance",
        "General Inquiry": "Customer Success",

        # Hour 16 classification evaluation categories
        "Cancellation": "Customer Success",
        "Complaint": "Customer Success",
        "Product Inquiry": "Product Support",
        "Refund": "Billing",
        "Sales": "Sales",
    }
)
