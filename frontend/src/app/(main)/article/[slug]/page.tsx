import Link from 'next/link';

export default async function ArticleDetailPage({ params }: { params: Promise<{ slug: string }> }) {
    const resolvedParams = await params;
    const res = await fetch(`http://backend:8000/api/articles/${resolvedParams.slug}/`, { cache: 'no-store' });
    const article = res.ok ? await res.json() : null;

    if (!article || article.error) {
        return (
            <div className="container mx-auto py-16 px-4 text-center min-h-[50vh] flex flex-col justify-center items-center">
                <h1 className="text-2xl font-bold text-gray-800 mb-4">Bài viết không tồn tại</h1>
                <Link href="/" className="text-blue-600 font-medium hover:underline">&larr; Quay lại trang chủ</Link>
            </div>
        );
    }

    return (
        <div className="bg-gray-50 min-h-screen pb-16">
            <style dangerouslySetInnerHTML={{__html: `
            .tinymce-content ul { list-style-type: disc !important; margin-left: 2rem !important; margin-bottom: 1.5rem !important; display: block !important; }
            .tinymce-content li { margin-bottom: 0.5rem !important; display: list-item !important; }
            .tinymce-content p { margin-bottom: 1.2rem !important; }
            .tinymce-content img { max-width: 100% !important; height: auto !important; border-radius: 0.75rem !important; margin: 2rem auto !important; display: block !important; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1) !important; }
        `}} />
            {article.thumbnail && (
                <div className="w-full md:h-[500px] h-[300px] relative bg-gray-100">
                    <img src={article.thumbnail} alt={article.title} className="w-full h-full object-cover" />
                </div>
            )}
            <div className="container mx-auto px-4 max-w-4xl -mt-20 relative z-10">
                <div className="bg-white rounded-2xl shadow-xl border border-gray-100 p-8 md:p-14">
                    {article.category_name && (
                        <div className="mb-6 text-center">
                            <span className="bg-blue-50 text-blue-600 px-4 py-1.5 rounded-full text-sm font-semibold uppercase tracking-wider">{article.category_name}</span>
                        </div>
                    )}
                    <h1 className="text-3xl md:text-5xl font-bold text-gray-900 mb-10 leading-tight text-center">{article.title}</h1>
                    
                    {/* KHỐI PHỤC HỒI ĐỊNH DẠNG TINYMCE */}
                    <div 
                        className="text-gray-800 text-lg leading-relaxed tinymce-content [&_p]:mb-6 [&_ul]:list-disc [&_ul]:ml-8 [&_ul]:mb-6 [&_ol]:list-decimal [&_ol]:ml-8 [&_ol]:mb-6 [&_li]:mb-2 [&_h2]:text-3xl [&_h2]:font-bold [&_h2]:mb-6 [&_h2]:text-blue-900 [&_h3]:text-2xl [&_h3]:font-semibold [&_h3]:mb-4 [&_img]:max-w-full [&_img]:h-auto [&_img]:mx-auto [&_img]:rounded-xl [&_img]:shadow-md [&_img]:my-8 [&_a]:text-blue-600 [&_a]:underline"
                        dangerouslySetInnerHTML={{ __html: article.content }}
                    />
                </div>
            </div>
        </div>
    );
}