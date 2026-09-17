from pydantic import BaseModel, Field, EmailStr

# Auth Schemas
class UserRegister(BaseModel):
    email: EmailStr
    password: str
    role: str = "analyst"

class UserLogin(BaseModel):
    email: EmailStr
    password: str

# ML Inference Schemas
class SupplyChainInput(BaseModel):
    Type: str
    Customer_Segment: str = Field(alias="Customer Segment")
    Shipping_Mode: str = Field(alias="Shipping Mode")
    Market: str
    Order_Region: str = Field(alias="Order Region")
    Category_Name: str = Field(alias="Category Name")
    Customer_City: str = Field(alias="Customer City")
    Customer_Country: str = Field(alias="Customer Country")
    Customer_State: str = Field(alias="Customer State")
    Order_City: str = Field(alias="Order City")
    Order_Country: str = Field(alias="Order Country")
    Order_State: str = Field(alias="Order State")
    Department_Name: str = Field(alias="Department Name")
    Order_Status: str = Field(alias="Order Status")
    order_date: str = Field(alias="order date (DateOrders)")
    Sales: float
    Order_Item_Quantity: int = Field(alias="Order Item Quantity")
    Order_Item_Product_Price: float = Field(alias="Order Item Product Price")
    Order_Item_Discount: float = Field(alias="Order Item Discount")
    Order_Item_Discount_Rate: float = Field(alias="Order Item Discount Rate")
    Sales_per_customer: float = Field(alias="Sales per customer")
    Order_Item_Total: float = Field(alias="Order Item Total")

    class Config:
        populate_by_name = True

class PredictionResponse(BaseModel):
    delayed: int
    delay_probability: float
    status: str