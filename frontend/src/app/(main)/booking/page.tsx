import { Suspense } from 'react';
import BookingForm from '@/components/BookingForm';

export default function Page() {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <BookingForm />
    </Suspense>
  );
}
