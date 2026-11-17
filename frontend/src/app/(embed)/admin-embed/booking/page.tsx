import { Suspense } from 'react';
import BookingForm from '@/components/BookingForm';

export default function Page() {
  return (
    <div className="w-full max-w-7xl mx-auto p-4 sm:p-6 lg:p-8">
      <Suspense fallback={
        <div className="flex items-center justify-center min-h-[400px]">
          <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-blue-600"></div>
        </div>
      }>
        <BookingForm />
      </Suspense>
    </div>
  );
}
