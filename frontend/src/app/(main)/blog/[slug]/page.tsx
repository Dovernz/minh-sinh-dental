import { notFound } from 'next/navigation';

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
            {article?.thumbnail && (
                <div className="w-full bg-gray-50 rounded-xl mb-8 flex justify-center">
                    <img 
                        src={article.thumbnail} 
                        alt={article.title} 
                        className="w-full h-auto max-h-[500px] object-contain rounded-xl shadow-sm border border-gray-100" 
                    />
                </div>
            )}
            <h1 className="text-4xl font-bold mb-6 text-gray-800">{article.title}</h1>
            <div 
                className="prose prose-lg prose-blue max-w-none text-gray-700" 
                dangerouslySetInnerHTML={{ __html: article.content }} 
            />
        </div>
    );
}
