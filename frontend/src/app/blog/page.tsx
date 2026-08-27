import Link from 'next/link';

export default function BlogPage() {
  // Dữ liệu giả lập (Mock data) để dựng giao diện
  const mockArticles = [
    { id: 1, title: 'Tầm quan trọng của việc cạo vôi răng định kỳ', category: 'Kiến thức nha khoa', date: '27/08/2026', image: 'https://placehold.co/600x400/e2e8f0/1e293b?text=Nha+Khoa+Minh+Sinh' },
    { id: 2, title: 'Niềng răng Invisalign có thực sự hiệu quả?', category: 'Chỉnh nha', date: '25/08/2026', image: 'https://placehold.co/600x400/e2e8f0/1e293b?text=Nha+Khoa+Minh+Sinh' },
    { id: 3, title: 'Ưu đãi 20% dịch vụ tẩy trắng răng mùa hè', category: 'Khuyến mãi', date: '20/08/2026', image: 'https://placehold.co/600x400/e2e8f0/1e293b?text=Nha+Khoa+Minh+Sinh' },
  ];

  return (
    <main className="min-h-screen bg-gray-50 py-16 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        <div className="text-center mb-16">
          <h1 className="text-4xl font-extrabold text-blue-900 tracking-tight sm:text-5xl">Góc tư vấn & Tin tức</h1>
          <p className="mt-4 text-xl text-gray-500 max-w-2xl mx-auto">Cập nhật những kiến thức nha khoa hữu ích và các chương trình ưu đãi mới nhất từ Minh Sinh.</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {mockArticles.map((article) => (
            <article key={article.id} className="bg-white rounded-2xl shadow-sm hover:shadow-lg transition-shadow duration-300 overflow-hidden border border-gray-100 flex flex-col">
              <div className="aspect-w-16 aspect-h-9 w-full overflow-hidden bg-gray-200">
                {/* Sử dụng thẻ img thường cho dữ liệu giả, sau này nối API sẽ dùng next/image */}
                <img src={article.image} alt={article.title} className="object-cover w-full h-48" />
              </div>
              <div className="p-6 flex-1 flex flex-col">
                <div className="flex items-center justify-between mb-3">
                  <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-blue-50 text-blue-700">{article.category}</span>
                  <span className="text-sm text-gray-500">{article.date}</span>
                </div>
                <h2 className="text-xl font-bold text-gray-900 mb-3 line-clamp-2">{article.title}</h2>
                <div className="mt-auto pt-4">
                  <Link href={`/blog/${article.id}`} className="text-blue-600 font-semibold hover:text-blue-800 transition">Đọc tiếp &rarr;</Link>
                </div>
              </div>
            </article>
          ))}
        </div>
      </div>
    </main>
  );
}
