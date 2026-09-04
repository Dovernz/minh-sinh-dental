import Link from 'next/link';

export default async function GlobalDynamicPage({ params }: { params: Promise<{ slug: string[] }> }) {
    const resolvedParams = await params;
    const currentUrl = '/' + resolvedParams.slug.join('/');

    const res = await fetch(`http://backend:8000/api/articles/by-url/?url=${currentUrl}`, { cache: 'no-store' });
    let data = { page_title: "", articles: [] };
    if (res.ok) {
        const json = await res.json();
        if (Array.isArray(json)) data.articles = json;
        else data = json;
    }

    const articles = data.articles || [];

    // Ưu tiên Tiêu đề từ Cấu hình Header, nếu không có mới tự động dịch từ URL
    let pageName = data.page_title;
    if (!pageName) {
        pageName = resolvedParams.slug[resolvedParams.slug.length - 1].replace(/-/g, ' ');
    }

    return (
        <div className="container mx-auto py-12 px-4 max-w-6xl">
            <h1 className="text-3xl md:text-4xl font-bold mb-12 text-blue-900 uppercase text-center tracking-wide">{pageName}</h1>
            
            {articles.length === 0 ? (
                <p className="text-gray-500 text-center">Nội dung chuyên mục này đang được cập nhật...</p>
            ) : (
                <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                    {articles.map((article: any) => (
                        <Link href={`/article/${article.slug}`} key={article.id} className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden hover:shadow-lg transition-all duration-300 flex flex-col h-full group block cursor-pointer">
                            {article.thumbnail && (
                                <div className="w-full h-48 relative bg-gray-100 overflow-hidden">
                                    <img src={article.thumbnail} alt={article.title} className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500" />
                                </div>
                            )}
                            <div className="p-6 flex-col flex flex-grow">
                                {article.category_name && (
                                    <div className="mb-4">
                                        <span className="inline-block w-fit bg-blue-50 text-blue-600 px-3 py-1 rounded-full text-xs font-semibold">{article.category_name}</span>
                                    </div>
                                )}
                                <h2 className="font-bold text-lg mb-4 text-gray-800 group-hover:text-blue-600 transition-colors line-clamp-3">{article.title}</h2>
                                <div className="mt-auto">
                                    <span className="text-blue-600 font-medium text-sm flex items-center gap-1 group-hover:translate-x-1 transition-transform">
                                        Đọc tiếp <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M17 8l4 4m0 0l-4 4m4-4H3"></path></svg>
                                    </span>
                                </div>
                            </div>
                        </Link>
                    ))}
                </div>
            )}
        </div>
    );
}