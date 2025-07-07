"""
Booking Tool for watsonx Orchestrate
Simulated booking functionality for educational purposes
"""

import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from ibm_watsonx_orchestrate.agent_builder.tools import tool
import random

# In a real implementation, this would connect to a booking system
# For educational purposes, we'll simulate the booking process

# Simulated booking storage
BOOKINGS = {}

@tool
def check_seat_availability(cinema_id: str,
                           film_id: str,
                           showtime: str,
                           date: str) -> Dict[str, Any]:
    """
    Check seat availability for a specific showtime (simulated)
    
    Args:
        cinema_id: Cinema identifier
        film_id: Film identifier
        showtime: Showtime in HH:MM format
        date: Date in YYYY-MM-DD format
    
    Returns:
        Dictionary containing seat map and availability
    """
    
    # Simulate seat map generation
    rows = ["A", "B", "C", "D", "E", "F", "G", "H", "J", "K"]
    seats_per_row = 14
    
    seat_map = []
    total_seats = 0
    available_seats = 0
    
    for row in rows:
        row_seats = []
        for seat_num in range(1, seats_per_row + 1):
            # Simulate some seats being already booked
            is_available = random.random() > 0.3  # 70% availability
            
            # Determine seat type based on row
            if row in ["E", "F", "G"]:
                seat_type = "premium"
                price = 15.00
            elif row in ["H", "J", "K"]:
                seat_type = "vip"
                price = 20.00
            else:
                seat_type = "standard"
                price = 12.00
            
            seat = {
                "row": row,
                "number": str(seat_num),
                "type": seat_type,
                "price": price,
                "available": is_available
            }
            
            row_seats.append(seat)
            total_seats += 1
            if is_available:
                available_seats += 1
        
        seat_map.append({
            "row": row,
            "seats": row_seats
        })
    
    return {
        "status": "success",
        "showtime_info": {
            "cinema_id": cinema_id,
            "film_id": film_id,
            "date": date,
            "time": showtime
        },
        "availability": {
            "total_seats": total_seats,
            "available_seats": available_seats,
            "occupancy_percentage": round((1 - available_seats/total_seats) * 100, 2)
        },
        "seat_map": seat_map,
        "pricing": {
            "standard": 12.00,
            "premium": 15.00,
            "vip": 20.00
        }
    }


@tool
def create_booking(cinema_id: str,
                  film_id: str,
                  film_title: str,
                  showtime: str,
                  date: str,
                  seats: List[Dict[str, str]],
                  customer_name: str,
                  customer_email: str,
                  customer_phone: str = "") -> Dict[str, Any]:
    """
    Create a booking for selected seats (simulated)
    
    Args:
        cinema_id: Cinema identifier
        film_id: Film identifier
        film_title: Film title for the booking
        showtime: Showtime in HH:MM format
        date: Date in YYYY-MM-DD format
        seats: List of seat selections [{"row": "A", "number": "5"}, ...]
        customer_name: Customer's full name
        customer_email: Customer's email address
        customer_phone: Optional customer phone number (empty string if not provided)
    
    Returns:
        Dictionary containing booking details and payment instructions
    """
    
    try:
        # Convert parameters to ensure correct types
        cinema_id = str(cinema_id)
        film_id = str(film_id)
        showtime = str(showtime)
        date = str(date)
        
        # Debug logging (remove in production)
        print(f"DEBUG: create_booking called with cinema_id={cinema_id}, film_id={film_id}, showtime={showtime}, date={date}, seats={seats}")
        
        # Validate inputs
        if not seats:
            return {"error": "No seats selected"}
        
        if len(seats) > 10:
            return {"error": "Maximum 10 seats per booking"}
        
        # Validate seat format
        for seat in seats:
            if not isinstance(seat, dict) or 'row' not in seat or 'number' not in seat:
                return {"error": "Invalid seat format. Each seat must have 'row' and 'number' fields."}
            # Ensure seat values are strings
            seat['row'] = str(seat['row'])
            seat['number'] = str(seat['number'])
        
        # Generate booking ID
        booking_id = f"BK-{uuid.uuid4().hex[:8].upper()}"
        
        # Calculate total price (simulated pricing)
        total_price = 0
        seat_details = []
        
        for seat in seats:
            row = seat.get("row", "")
            number = seat.get("number", "")
            
            # Determine seat price based on row
            if row in ["E", "F", "G"]:
                price = 15.00
                seat_type = "premium"
            elif row in ["H", "J", "K"]:
                price = 20.00
                seat_type = "vip"
            else:
                price = 12.00
                seat_type = "standard"
            
            total_price += price
            seat_details.append({
                "row": row,
                "number": number,
                "type": seat_type,
                "price": price
            })
        
        # Create booking record
        booking = {
            "booking_id": booking_id,
            "status": "pending_payment",
            "cinema_id": cinema_id,
            "film_id": film_id,
            "film_title": film_title,
            "showtime": f"{date} {showtime}",
            "seats": seat_details,
            "customer": {
                "name": customer_name,
                "email": customer_email,
                "phone": customer_phone if customer_phone else None
            },
            "pricing": {
                "subtotal": total_price,
                "booking_fee": 1.50,
                "total": total_price + 1.50
            },
            "created_at": datetime.now().isoformat(),
            "expires_at": (datetime.now() + timedelta(minutes=10)).isoformat()
        }
        
        # Store booking (in real implementation, this would be in a database)
        BOOKINGS[booking_id] = booking
        
        return {
            "status": "success",
            "booking_id": booking_id,
            "booking_details": booking,
            "payment_required": True,
            "payment_instructions": "Please complete payment within 10 minutes to confirm your booking.",
            "payment_url": f"https://cinema-booking.example.com/payment/{booking_id}"  # Simulated
        }
    
    except Exception as e:
        return {
            "status": "error",
            "error": f"Booking creation failed: {str(e)}",
            "debug_info": f"Parameters received: cinema_id={cinema_id}, film_id={film_id}, showtime={showtime}, date={date}"
        }


@tool
def process_payment(booking_id: str,
                   payment_method: str = "card",
                   card_last_four: str = "") -> Dict[str, Any]:
    """
    Process payment for a booking (simulated)
    
    Args:
        booking_id: Booking identifier
        payment_method: Payment method (card, paypal, etc.)
        card_last_four: Last 4 digits of card (empty string if not provided)
    
    Returns:
        Dictionary containing payment confirmation
    """
    
    # Retrieve booking
    booking = BOOKINGS.get(booking_id)
    
    if not booking:
        return {"error": "Booking not found"}
    
    if booking["status"] != "pending_payment":
        return {"error": f"Booking is already {booking['status']}"}
    
    # Check if booking has expired
    expires_at = datetime.fromisoformat(booking["expires_at"])
    if datetime.now() > expires_at:
        booking["status"] = "expired"
        return {"error": "Booking has expired. Please create a new booking."}
    
    # Simulate payment processing
    payment_success = random.random() > 0.05  # 95% success rate
    
    if payment_success:
        # Generate confirmation code
        confirmation_code = f"CNF-{uuid.uuid4().hex[:6].upper()}"
        
        # Update booking status
        booking["status"] = "confirmed"
        booking["confirmation_code"] = confirmation_code
        booking["payment"] = {
            "method": payment_method,
            "transaction_id": f"TXN-{uuid.uuid4().hex[:10].upper()}",
            "processed_at": datetime.now().isoformat(),
            "amount": booking["pricing"]["total"]
        }
        
        if card_last_four and card_last_four.strip():
            booking["payment"]["card_last_four"] = card_last_four
        
        # Generate tickets (simulated)
        tickets = []
        for seat in booking["seats"]:
            ticket = {
                "ticket_id": f"TKT-{uuid.uuid4().hex[:8].upper()}",
                "seat": f"{seat['row']}{seat['number']}",
                "qr_code": f"https://cinema-booking.example.com/qr/{uuid.uuid4().hex}"  # Simulated
            }
            tickets.append(ticket)
        
        booking["tickets"] = tickets
        
        return {
            "status": "success",
            "confirmation_code": confirmation_code,
            "booking_id": booking_id,
            "payment": booking["payment"],
            "tickets": tickets,
            "message": "Payment successful! Your tickets have been emailed to you.",
            "booking_details": {
                "film": booking["film_title"],
                "showtime": booking["showtime"],
                "seats": [f"{s['row']}{s['number']}" for s in booking["seats"]],
                "total_paid": booking["pricing"]["total"]
            }
        }
    else:
        return {
            "status": "failed",
            "error": "Payment declined. Please try another payment method.",
            "booking_id": booking_id
        }


@tool
def get_booking_status(booking_id: str) -> Dict[str, Any]:
    """
    Retrieve booking details and status
    
    Args:
        booking_id: Booking identifier
    
    Returns:
        Dictionary containing booking information
    """
    
    booking = BOOKINGS.get(booking_id)
    
    if not booking:
        return {"error": "Booking not found"}
    
    # Remove sensitive payment details for display
    display_booking = booking.copy()
    if "payment" in display_booking and "card_last_four" in display_booking["payment"]:
        display_booking["payment"]["card_masked"] = f"****{display_booking['payment']['card_last_four']}"
        del display_booking["payment"]["card_last_four"]
    
    return {
        "status": "success",
        "booking": display_booking
    }