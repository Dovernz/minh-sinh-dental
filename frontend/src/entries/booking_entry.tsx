import React from 'react';
import { createRoot } from 'react-dom/client';
import BookingForm from '../components/BookingForm';

const container = document.getElementById('booking-root');
if (container) {
  const root = createRoot(container);
  root.render(<BookingForm />);
}
