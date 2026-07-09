from app.rag import chunk_document, store_chunks

# Business mock data as requested
MOCK_BANK_DATA = """
# National Bank Employee Guidelines
## Dress Code
All employees at the National Bank branches must adhere to a business professional dress code. This includes suits, ties, and formal wear.

## Work Hours
Standard operating hours for bank tellers are 8:00 AM to 5:00 PM, Monday through Friday. Weekend shifts are on rotation.
"""

MOCK_STORE_DATA = """
# MegaShopping Store Inventory Procedures
## Stock Intake
When new inventory arrives at the loading dock, store associates must log the barcode shipments into the central ledger system within 2 hours.

## Customer Returns
Any item returned by a customer must be inspected for damages. If the item is intact, it can be restocked on the shelves with a 10% discount tag.
"""

def seed_database():
    print("Seeding database with business examples...")
    bank_chunks = chunk_document(MOCK_BANK_DATA)
    store_chunks("https://internal.bank.local/guidelines", bank_chunks)
    
    shopping_chunks = chunk_document(MOCK_STORE_DATA)
    store_chunks("https://internal.store.local/procedures", shopping_chunks)
    
    print("Seeding complete.")

if __name__ == "__main__":
    seed_database()
