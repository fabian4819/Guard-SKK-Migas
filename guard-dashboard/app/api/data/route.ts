import { NextRequest, NextResponse } from 'next/server';
import { loadCSVData, getDataStatistics } from '@/lib/dataLoader';

export async function GET(request: NextRequest) {
  const searchParams = request.nextUrl.searchParams;
  const startDate = searchParams.get('startDate') || undefined;
  const endDate = searchParams.get('endDate') || undefined;
  const limit = parseInt(searchParams.get('limit') || '0');
  const offset = parseInt(searchParams.get('offset') || '0');

  try {
    const data = loadCSVData(startDate, endDate);

    if (data.length === 0) {
      return NextResponse.json(
        { error: 'No data found' },
        { status: 404 }
      );
    }

    // Apply pagination if limit is specified
    const paginatedData = limit > 0
      ? data.slice(offset, offset + limit)
      : data;

    const statistics = getDataStatistics(data);

    return NextResponse.json({
      data: paginatedData,
      statistics,
      total: data.length,
      offset,
      limit: limit || data.length,
    });
  } catch (error) {
    console.error('API Error:', error);
    return NextResponse.json(
      { error: 'Failed to load data' },
      { status: 500 }
    );
  }
}

export const dynamic = 'force-dynamic';
