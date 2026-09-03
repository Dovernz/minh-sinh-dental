export const dynamic = 'force-dynamic';

async function getDraftArticle(slug: string, previewToken: string) {
    try {
        const res = await fetch(`http://backend:8000/api/articles/${slug}/?preview=${previewToken}`, { 
            cache: 'no-store',
            headers: { 'Content-Type': 'application/json' }
        });
        if (!res.ok) return null;
        return await res.json();
    } catch (error) {
        console.error("Lỗi Fetch API Backend:", error);
        return null;
    }
}

export default async function BlogDemoPage(props: any) {
    // Giải nén Promise cho chuẩn Next.js mới
    const searchParams = await props.searchParams;
    const params = await props.params;

    if (searchParams?.preview !== 'admin_secret_123') {
        return <div className="p-10 text-center text-red-600 font-bold text-2xl">Sai Token bảo mật. Cửa đã khóa!</div>;
    }

    const article = await getDraftArticle(params.slug, searchParams.preview);

    if (!article) {
        return <div className="p-10 text-center text-red-600 font-bold text-2xl">Không tìm thấy bài viết hoặc Backend từ chối kết nối!</div>;
    }

    return (
        <main className="max-w-4xl mx-auto py-12 px-6 mt-10 bg-white shadow-sm rounded-xl relative border-2 border-red-400">
            <div className="absolute top-0 left-0 w-full bg-red-500 text-white text-center py-1 text-sm font-bold rounded-t-lg">
                CHẾ ĐỘ XEM TRƯỚC (BẢN NHÁP) - KHÔNG HIỂN THỊ VỚI KHÁCH HÀNG
            </div>
            
            {article?.thumbnail && (
                <div className="w-full bg-gray-50 rounded-xl mb-8 mt-8 flex justify-center">
                    <img 
                        src={article.thumbnail} 
                        alt={article.title} 
                        className="w-full h-auto max-h-[500px] object-contain rounded-xl shadow-sm border border-gray-100" 
                    />
                </div>
            )}

            <h1 className="text-4xl font-extrabold mb-8 mt-6 text-gray-900">{article?.title || 'Chưa có tiêu đề'}</h1>
            <div className="prose prose-lg prose-blue max-w-none text-gray-700" dangerouslySetInnerHTML={{ __html: article?.content || '<p>Nội dung trống</p>' }} />
        </main>
    );
}
