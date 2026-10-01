import Odontogram from '@/components/Odontogram';

export const metadata = {
    title: 'Dental Chart | Minh Sinh',
};

export default function DentalChartPage() {
    return (
        <main className="min-h-screen bg-gray-100 p-4">
            <Odontogram customerId="preview" />
        </main>
    );
}
