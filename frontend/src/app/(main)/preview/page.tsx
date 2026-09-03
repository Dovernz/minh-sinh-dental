'use client';
import { useEffect, useState } from 'react';

export default function PreviewPage() {
    const [data, setData] = useState({ title: '', content: '' });

    useEffect(() => {
        const handleMessage = (event: MessageEvent) => {
            if (event.data?.type === 'LIVE_PREVIEW') {
                setData({
                    title: event.data.title || 'Tiêu đề bài viết...',
                    content: event.data.content || '<p>Nội dung sẽ hiển thị ở đây...</p>'
                });
            }
        };
        window.addEventListener('message', handleMessage);
        return () => window.removeEventListener('message', handleMessage);
    }, []);

    return (
        <div className="max-w-4xl mx-auto p-8 bg-white shadow-lg mt-10 rounded-xl">
            <h1 className="text-4xl font-bold mb-6 text-gray-800">{data.title}</h1>
            <div 
                className="prose prose-lg max-w-none"
                dangerouslySetInnerHTML={{ __html: data.content }}
            />
        </div>
    );
}
