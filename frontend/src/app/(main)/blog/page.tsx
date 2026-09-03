import Link from 'next/link';

async function getArticles(category?: string) {
    const url = category 
        ? `http://backend:8000/api/articles/?category=${category}` 
        : `http://backend:8000/api/articles/`;
    const res = await fetch(url, { cache: 'no-store' });
    if (!res.ok) return [];
    return res.json();
}

export default async function BlogPage(props: any) {
    const searchParams = await props.searchParams;
    const category = searchParams?.category;

    const articles = await getArticles(category);

    return (
        <main className="min-h-screen bg-gray-50 py-16 px-4 sm:px-6 lg:px-8">
            <div className="max-w-7xl mx-auto">
                <div className="text-center mb-16">
                    <h1 className="text-4xl font-extrabold text-blue-900 tracking-tight sm:text-5xl">Góc tư vấn & Tin tức</h1>
                    <p className="mt-4 text-xl text-gray-500 max-w-2xl mx-auto">Cập nhật những kiến thức nha khoa hữu ích và các chương trình ưu đãi mới nhất từ Minh Sinh.</p>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                    {articles.map((article: any) => (
                        <Link href={`/blog/${article.slug}`} key={article.id} className="group block bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden hover:shadow-lg transition-all duration-300 flex flex-col">
                            <div className="w-full h-60 bg-gray-50 overflow-hidden relative">
                                <img
                                    src={article.thumbnail || 'https://placehold.co/600x400/e2e8f0/1e293b?text=No+Image'}
                                    alt={article.title}
                                    className="w-full h-full object-cover object-center group-hover:scale-105 transition-transform duration-500 ease-out"
                                />
                            </div>
                            <div className="p-6 flex-1 flex flex-col">
                                <span className="text-xs font-semibold text-blue-600 bg-blue-50 inline-block w-fit px-3 py-1 rounded-full mb-4">
                                    {article.category === 'khuyen-mai' ? 'Khuyến mại' : 'Kiến thức y khoa'}
                                </span>
                                <h2 className="text-xl font-bold text-gray-900 mb-3 group-hover:text-blue-600 transition-colors line-clamp-2">{article.title}</h2>
                                <div className="text-blue-600 font-medium text-sm flex items-center mt-auto pt-4">
                                    Đọc tiếp <span className="ml-1 group-hover:translate-x-1 transition-transform">→</span>
                                </div>
                            </div>
                        </Link>
                    ))}
                </div>
                
                {articles.length === 0 && (
                    <div className="text-center text-gray-500 py-20 text-xl font-medium">Chưa có bài viết nào trong chuyên mục này.</div>
                )}
            </div>
        </main>
    );
}
