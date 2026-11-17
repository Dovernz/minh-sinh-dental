import { Suspense } from 'react';
import BookingForm from '@/components/BookingForm';

export default function Page() {
  return (
    <main className="w-full min-h-screen bg-slate-50/60 py-4 sm:py-8 px-2 sm:px-6 lg:px-8 overflow-x-hidden">
      <div className="w-full max-w-7xl mx-auto overflow-x-hidden">
        <Suspense fallback={
          <div className="flex items-center justify-center min-h-[500px]">
            <div className="text-center">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
              <p className="text-gray-600 font-medium">Đang tải biểu mẫu đặt lịch khám...</p>
            </div>
          </div>
        }>
          <BookingForm />
        </Suspense>
      </div>
    </main>
  );
}
