import { NextRequest, NextResponse } from 'next/server';
import * as nodemailer from 'nodemailer';
import { generateRCAPDF } from '@/lib/pdfGenerator';
import pdfMake from 'pdfmake/build/pdfmake';
import pdfFonts from 'pdfmake/build/vfs_fonts';

// Initialize pdfMake with fonts
pdfMake.vfs = pdfFonts.pdfMake.vfs;

async function generatePDFBuffer(anomalyData: any): Promise<Buffer> {
  return new Promise((resolve, reject) => {
    try {
      const docDefinition = generateRCAPDF(anomalyData);
      const pdfDocGenerator = pdfMake.createPdf(docDefinition);

      pdfDocGenerator.getBuffer((buffer: Buffer) => {
        resolve(buffer);
      });
    } catch (error) {
      reject(error);
    }
  });
}

export async function POST(request: NextRequest) {
  try {
    const { anomalies, alertEmail } = await request.json();
    const anomalyList = Array.isArray(anomalies) ? anomalies : [anomalies];

    // Validate custom email address
    if (!alertEmail || !alertEmail.includes('@')) {
      return NextResponse.json(
        { error: 'Valid email address is required' },
        { status: 400 }
      );
    }

    // Check email configuration
    const smtpServer = process.env.SMTP_SERVER;
    const smtpPort = process.env.SMTP_PORT;
    const smtpUser = process.env.SMTP_USERNAME;
    const smtpPassword = process.env.SMTP_PASSWORD;
    const alertFrom = process.env.ALERT_FROM;

    if (!smtpServer || !smtpUser || !smtpPassword) {
      return NextResponse.json(
        { error: 'SMTP configuration not found in .env' },
        { status: 400 }
      );
    }

    // Create transporter
    const transporter = nodemailer.createTransport({
      host: smtpServer,
      port: parseInt(smtpPort || '587'),
      secure: false,
      auth: {
        user: smtpUser,
        pass: smtpPassword,
      },
    });

    // Format batch details
    const firstAnomaly = anomalyList[0];
    const lastAnomaly = anomalyList[anomalyList.length - 1];
    const timeRange = anomalyList.length > 1
      ? `${new Date(firstAnomaly.datetime).toLocaleTimeString()} - ${new Date(lastAnomaly.datetime).toLocaleTimeString()}`
      : new Date(firstAnomaly.datetime).toLocaleString();

    const anomalySummaryRows = anomalyList.map((anomalyData: any, index: number) => {
      const timestamp = new Date(anomalyData.datetime).toLocaleString('en-US', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
        hour12: false
      }).replace(',', '');
      const thresholdRatio = anomalyData.threshold_ratio.toFixed(1);
      const exceedPercent = (anomalyData.threshold_ratio - 100).toFixed(1);
      const status = anomalyData.threshold_ratio > 150 ? 'CRITICAL' :
                     anomalyData.threshold_ratio > 120 ? 'WARNING' : 'CAUTION';

      return `
        <tr style="background-color: ${index % 2 === 0 ? '#f9f9f9' : '#ffffff'};">
          <td style="padding: 10px; border-bottom: 1px solid #e0e0e0; text-align: center;">
            ${index + 1}
          </td>
          <td style="padding: 10px; border-bottom: 1px solid #e0e0e0;">
            ${timestamp}
          </td>
          <td style="padding: 10px; border-bottom: 1px solid #e0e0e0; text-align: right;">
            ${thresholdRatio}%
            <span style="color: #d32f2f; font-size: 11px; display: block;">
              (Reconstruction loss exceeds threshold by ${exceedPercent}%)
            </span>
          </td>
          <td style="padding: 10px; border-bottom: 1px solid #e0e0e0;">
            ${status}
          </td>
        </tr>
      `;
    }).join('');

    // Email HTML
    const emailHtml = `
      <!DOCTYPE html>
      <html>
      <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
      </head>
      <body style="margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;">
        <div style="max-width: 800px; margin: 0 auto; background-color: #ffffff;">
          <div style="background-color: #1976d2; color: white; padding: 20px;">
            <h1 style="margin: 0; font-size: 18px; font-weight: 500;">
              [CPP Donggi] ANOMALY DETECTION - BOOSTER COMPRESSOR B CPP DONGGI
            </h1>
            <p style="margin: 8px 0 0 0; font-size: 12px; opacity: 0.9;">
              GUARD (Generative Understanding for Anomaly Response & Detection)
            </p>
          </div>
          <div style="padding: 24px;">
            <p style="color: #333; line-height: 1.6; margin-bottom: 24px;">
              An abnormal condition has been detected in the process parameters of the
              <strong>BOOSTER COMPRESSOR B CPP DONGGI</strong>. The details are as follows:
            </p>
            ${anomalyList.length > 1 ? `
            <div style="background-color: #fff3e0; border-left: 4px solid #ff9800; padding: 16px; margin-bottom: 24px;">
              <h3 style="margin: 0 0 8px 0; color: #e65100; font-size: 16px;">Batch Summary</h3>
              <ul style="margin: 0; padding-left: 20px; color: #333;">
                <li><strong>Total Anomalies:</strong> ${anomalyList.length}</li>
                <li><strong>Time Range:</strong> ${timeRange}</li>
                <li><strong>PDF Attachments:</strong> ${anomalyList.length} detailed reports attached</li>
              </ul>
            </div>
            ` : ''}
            <h2 style="color: #333; font-size: 20px; margin-bottom: 16px; margin-top: 32px;">
              Anomaly Details
            </h2>
            <table style="width: 100%; border-collapse: collapse; margin-top: 16px; background-color: #fafafa;">
              <thead>
                <tr style="background-color: #e0e0e0;">
                  <th style="padding: 12px; text-align: center; font-weight: 600; border-bottom: 2px solid #bdbdbd; width: 50px;">#</th>
                  <th style="padding: 12px; text-align: left; font-weight: 600; border-bottom: 2px solid #bdbdbd;">Timestamp</th>
                  <th style="padding: 12px; text-align: right; font-weight: 600; border-bottom: 2px solid #bdbdbd;">Threshold ratio</th>
                  <th style="padding: 12px; text-align: left; font-weight: 600; border-bottom: 2px solid #bdbdbd;">Asset integrity status</th>
                </tr>
              </thead>
              <tbody>
                ${anomalySummaryRows}
              </tbody>
            </table>
            <p style="color: #666; font-size: 12px; margin-top: 16px; font-style: italic;">
              *Each anomaly has a detailed PDF report attached with variable analysis and root cause scenarios.
            </p>
            <div style="margin-top: 40px; padding-top: 20px; border-top: 1px solid #e0e0e0;">
              <p style="color: #666; font-size: 12px; margin: 0;">
                This is an automated alert from GUARD (Generative Understanding for Anomaly Response & Detection).
              </p>
              <p style="color: #666; font-size: 12px; margin: 8px 0 0 0;">
                Generated at: ${new Date().toISOString().replace('T', ' ').substring(0, 19)}
              </p>
            </div>
          </div>
        </div>
      </body>
      </html>
    `;

    // Generate PDFs using TypeScript/pdfmake
    console.log(`📄 Generating ${anomalyList.length} PDF(s) using pdfmake...`);
    const pdfAttachments = await Promise.all(
      anomalyList.map(async (anomalyData: any, index: number) => {
        const pdfBuffer = await generatePDFBuffer(anomalyData);
        const timestampStr = new Date(anomalyData.datetime).toISOString().replace(/:/g, '-').substring(0, 19);
        const pdfFilename = `RCA_Report_${index + 1}_${timestampStr}.pdf`;

        return {
          filename: pdfFilename,
          content: pdfBuffer,
          contentType: 'application/pdf'
        };
      })
    );

    // Send ONE email with all PDF attachments
    const subject = anomalyList.length > 1
      ? `🚨 GUARD BATCH ALERT - ${anomalyList.length} Anomalies Detected`
      : `🚨 GUARD ANOMALY ALERT - ${new Date(firstAnomaly.datetime).toLocaleString()}`;

    await transporter.sendMail({
      from: `"GUARD Alert System" <${alertFrom || smtpUser}>`,
      to: alertEmail,
      subject: subject,
      html: emailHtml,
      attachments: pdfAttachments
    });

    return NextResponse.json({
      success: true,
      message: `Email sent successfully with ${anomalyList.length} PDF attachment${anomalyList.length > 1 ? 's' : ''}`
    });
  } catch (error: any) {
    console.error('Error sending email:', error);
    return NextResponse.json(
      {
        error: error?.message || 'Failed to send email',
        details: error?.stack || 'Unknown error'
      },
      { status: 500 }
    );
  }
}

export const dynamic = 'force-dynamic';
