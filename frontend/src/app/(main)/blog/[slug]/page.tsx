import { notFound } from 'next/navigation';

import { Metadata } from 'next';

export async function generateMetadata(props: any): Promise<Metadata> {
    const params = await props.params;
    const res = await fetch(`http://backend:8000/api/articles/${params.slug}/`);
    if (!res.ok) return { title: 'Bài viết không tồn tại' };
    const article = await res.json();
    
    // Fallback image if thumbnail is empty
    const imgUrl = article.thumbnail || 'https://placehold.co/600x400/e2e8f0/1e293b?text=Nha+Khoa+Minh+Sinh';
    
    return {
        title: `${article.title} | Nha Khoa Minh Sinh`,
        description: article.content ? article.content.replace(/<[^>]+>/g, '').substring(0, 160) + '...' : '',
        openGraph: {
            title: article.title,
            images: [imgUrl],
        },
    };
}


async function getArticle(slug: string) {
    const res = await fetch(`http://backend:8000/api/articles/${slug}/`);
    if (!res.ok) {
        return null;
    }
    return res.json();
}

export default async function ArticlePage(props: any) {
    const params = await props.params;
    const article = await getArticle(params.slug);

    if (!article) {
        notFound();
    }

    return (
        <div className="max-w-4xl mx-auto py-10 px-4 mt-10 bg-white shadow-lg rounded-xl">
            
            <h1 className="text-4xl font-bold mb-6 text-gray-800">{article.title}</h1>
            <div 
                className="prose prose-lg prose-blue max-w-none text-gray-700 prose-p:leading-relaxed prose-li:marker:text-blue-500" 
                dangerouslySetInnerHTML={{ __html: article.content }} 
            />
        </div>
    );
}
