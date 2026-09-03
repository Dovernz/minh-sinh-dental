import { NextRequest, NextResponse } from 'next/server';
import { revalidatePath } from 'next/cache';

export async function POST(request: NextRequest) {
    const secret = request.nextUrl.searchParams.get('secret');
    const slug = request.nextUrl.searchParams.get('slug');

    // Kiểm tra token bảo mật để tránh bị spam gọi API
    if (secret !== 'revalidate_secret_123') {
        return NextResponse.json({ message: 'Sai token bảo mật' }, { status: 401 });
    }
    if (!slug) {
        return NextResponse.json({ message: 'Thiếu slug bài viết' }, { status: 400 });
    }

    try {
        // Xóa cache tĩnh của trang bài viết cụ thể và trang danh sách Blog tổng
        revalidatePath(`/blog/${slug}`);
        revalidatePath('/blog');
        return NextResponse.json({ revalidated: true, now: Date.now() });
    } catch (err) {
        return NextResponse.json({ message: 'Lỗi khi xóa cache' }, { status: 500 });
    }
}
