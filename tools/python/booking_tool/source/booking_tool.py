"""
Booking Tool for watsonx Orchestrate
Simulated booking functionality for educational purposes
"""

import uuid
from typing import List, Dict, Any
from datetime import datetime, timedelta
from ibm_watsonx_orchestrate.agent_builder.tools import tool
import random

# Simulated booking storage
BOOKINGS = {}

@tool
def check_seat_availability(cinema_id: str,
                           film_id: str,
                           showtime: str,
                           date: str) -> Dict[str, Any]:
    """
    Check seat availability for a specific showtime (simulated)
    """
    
    # Simulate seat map generation
    rows = ["A", "B", "C", "D", "E", "F"]
    seats_per_row = 10
    
    seat_map = []
    total_seats = 0
    available_seats = 0
    
    for row in rows:
        row_seats = []
        for seat_num in range(1, seats_per_row + 1):
            is_available = random.random() > 0.3  # 70% availability
            
            if row in ["E", "F"]:
                seat_type = "premium"
                price = 15.00
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
            "available_seats": available_seats
        },
        "seat_map": seat_map,
        "pricing": {
            "standard": 12.00,
            "premium": 15.00
        }
    }


@tool
def create_booking(customer_name: str,
                  customer_email: str,
                  film_title: str,
                  showtime: str,
                  seat_count: int = 2) -> Dict[str, Any]:
    """
    Create a booking for movie tickets (simplified)
    
    Args:
        customer_name: Customer's full name
        customer_email: Customer's email address
        film_title: Name of the movie
        showtime: Time of the showing
        seat_count: Number of seats to book (default: 2)
    
    Returns:
        Dictionary containing booking confirmation
    """
    
    try:
        # Generate booking ID
        booking_id = f"BK-{uuid.uuid4().hex[:8].upper()}"
        
        # Calculate pricing
        price_per_seat = 12.00
        total_price = price_per_seat * seat_count
        booking_fee = 1.50
        final_total = total_price + booking_fee
        
        # Generate seats automatically
        seats = []
        for i in range(seat_count):
            seats.append({
                "row": "A",
                "number": str(i + 1),
                "type": "standard",
                "price": price_per_seat
            })
        
        # Create booking record
        booking = {
            "booking_id": booking_id,
            "status": "confirmed",
            "film_title": film_title,
            "showtime": showtime,
            "seats": seats,
            "customer": {
                "name": customer_name,
                "email": customer_email
            },
            "pricing": {
                "subtotal": total_price,
                "booking_fee": booking_fee,
                "total": final_total
            },
            "created_at": datetime.now().isoformat()
        }
        
        # Store booking
        BOOKINGS[booking_id] = booking
        
        return {
            "status": "success",
            "booking_id": booking_id,
            "message": f"Booking confirmed for {seat_count} seats for '{film_title}' at {showtime}",
            "confirmation_details": {
                "booking_id": booking_id,
                "customer": customer_name,
                "film": film_title,
                "showtime": showtime,
                "seats": f"{seat_count} seats in row A",
                "total_cost": f"€{final_total:.2f}",
                "confirmation_email": f"Confirmation sent to {customer_email}"
            }
        }
    
    except Exception as e:
        return {
            "status": "error",
            "error": f"Booking failed: {str(e)}"
        }


@tool
def get_booking_status(booking_id: str) -> Dict[str, Any]:
    """
    Retrieve booking details
    
    Args:
        booking_id: Booking identifier
    
    Returns:
        Dictionary containing booking information
    """
    
    booking = BOOKINGS.get(booking_id)
    
    if not booking:
        return {"error": "Booking not found"}
    
    return {
        "status": "success",
        "booking": booking
    }


@tool
def process_payment(booking_id: str) -> Dict[str, Any]:
    """
    Process payment for a booking (simulated)
    
    Args:
        booking_id: Booking identifier
    
    Returns:
        Dictionary containing payment confirmation
    """
    
    booking = BOOKINGS.get(booking_id)
    
    if not booking:
        return {"error": "Booking not found"}
    
    # Simulate payment processing
    payment_success = True  # Always succeed for demo
    
    if payment_success:
        # Generate confirmation code
        confirmation_code = f"CNF-{uuid.uuid4().hex[:6].upper()}"
        
        # Update booking
        booking["status"] = "paid"
        booking["confirmation_code"] = confirmation_code
        booking["payment_processed_at"] = datetime.now().isoformat()
        
        return {
            "status": "success",
            "confirmation_code": confirmation_code,
            "message": "Payment successful! Enjoy your movie!",
            "booking_details": {
                "film": booking["film_title"],
                "showtime": booking["showtime"],
                "total_paid": f"€{booking['pricing']['total']:.2f}"
            }
        }
    else:
        return {
            "status": "failed",
            "error": "Payment declined"
        }