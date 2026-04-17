import { NextRequest, NextResponse } from 'next/server';
import * as nodemailer from 'nodemailer';
import { jsPDF } from 'jspdf';
import autoTable from 'jspdf-autotable';
import { rcaKnowledgeBase } from '@/lib/rcaKnowledgeBase';

async function generateRCAPDF(anomalyData: any): Promise<Buffer> {
  const doc = new jsPDF({ orientation: 'landscape', unit: 'mm', format: 'a4' });

  const timestamp = new Date(anomalyData.datetime).toLocaleDateString('en-US', {
    day: 'numeric',
    month: 'long',
    year: 'numeric',
  });

  // Title
  doc.setFontSize(14);
  doc.setTextColor(25, 118, 210);
  doc.text('ANOMALY DETECTION BOOSTER COMPRESSOR B CPP DONGGI', doc.internal.pageSize.getWidth() / 2, 15, { align: 'center' });

  // Header info
  doc.setFontSize(9);
  doc.setTextColor(0, 0, 0);
  doc.setFont('helvetica', 'bold');
  doc.text('Equipment:', 15, 25);
  doc.text('Timestamp:', 200, 25);
  doc.setFont('helvetica', 'normal');
  doc.text('BOOSTER COMPRESSOR B CPP DONGGI', 40, 25);
  doc.text(timestamp, 225, 25);
  doc.setFont('helvetica', 'bold');
  doc.text('Location:', 15, 30);
  doc.setFont('helvetica', 'normal');
  doc.text('CPP Donggi', 40, 30);

  // Table 1: Variable Analysis
  const sensors = {
    Flow_Rate: { tag: 'FI1001B', unit: 'MMSCFD', low: 45, high: 56 },
    Suction_Pressure: { tag: 'PI1001B', unit: 'barg', low: 33, high: 34 },
    Discharge_Pressure: { tag: 'PI1004B', unit: 'barg', low: 60, high: 63.3 },
    Suction_Temperature: { tag: 'TI1003B', unit: '°C', low: 90, high: 100 },
    Discharge_Temperature: { tag: 'TI1004B', unit: '°C', low: 189, high: 205 },
  };

  const tableData = Object.entries(sensors).map(([key, config]) => {
    const value = anomalyData[key] || 0;
    const expected = (config.low + config.high) / 2;
    const deviation = value - expected;
    const deviationPct = (deviation / expected) * 100;
    const contribution = anomalyData[`contrib_${key}`] || 0;

    const isOutOfRange = value < config.low || value > config.high;
    const abnormality = isOutOfRange || Math.abs(deviationPct) > 2 || contribution > 20 ? 'YES' : 'NO';

    return [
      key.replace('_', ' '),
      config.tag,
      value.toFixed(2),
      expected.toFixed(2),
      deviation.toFixed(2),
      `${deviationPct > 0 ? '+' : ''}${deviationPct.toFixed(1)}%`,
      `${contribution.toFixed(1)}%`,
      abnormality
    ];
  });

  autoTable(doc, {
    startY: 40,
    head: [['VARIABLE', 'TAG', 'ACTUAL\nVALUE', 'EXPECTED\nVALUE', 'DEVIATION', 'DEVIATION\n%', 'LOSS\nCONTRIB', 'ABNORMALITY']],
    body: tableData,
    theme: 'grid',
    headStyles: { fillColor: [68, 114, 196], textColor: [255, 255, 255], fontSize: 8, halign: 'center' },
    bodyStyles: { fontSize: 8 },
    alternateRowStyles: { fillColor: [242, 242, 242] },
    columnStyles: {
      0: { cellWidth: 35 },
      1: { cellWidth: 25 },
      2: { cellWidth: 25, halign: 'right' },
      3: { cellWidth: 25, halign: 'right' },
      4: { cellWidth: 25, halign: 'right' },
      5: { cellWidth: 25, halign: 'right' },
      6: { cellWidth: 25, halign: 'right' },
      7: { cellWidth: 25, halign: 'center' }
    }
  });

  // @ts-ignore - autoTable adds finalY property
  let finalY = doc.lastAutoTable.finalY + 10;

  // Table 2: RCA Scenarios
  doc.setFontSize(10);
  doc.setTextColor(0, 0, 0);
  doc.text('ROOT CAUSE ANALYSIS - PROBABLE SCENARIOS', 15, finalY);

  // Match RCA scenarios based on abnormal sensors
  const matchedScenarios = rcaKnowledgeBase
    .map(scenario => {
      let matchScore = 0;

      // Check each sensor against scenario
      Object.entries(sensors).forEach(([key, config]) => {
        const value = anomalyData[key] || 0;
        const isOutOfRange = value < config.low || value > config.high;

        if (isOutOfRange && scenario[key as keyof typeof scenario]) {
          matchScore += 3; // Increase score if scenario matches abnormal sensor
        }
      });

      return { ...scenario, matchScore };
    })
    .filter(s => s.matchScore > 0)
    .sort((a, b) => b.matchScore - a.matchScore)
    .slice(0, 5); // Top 5 scenarios

  // If no matches, show top 5 general scenarios
  const scenariosToShow = matchedScenarios.length > 0
    ? matchedScenarios
    : rcaKnowledgeBase.slice(0, 5);

  const rcaTableData = scenariosToShow.map(scenario => [
    scenario.division,
    scenario.prob,
    scenario.rca,
    scenario.actions,
    scenario.Flow_Rate ? 'YES' : 'NO',
    scenario.Suction_Pressure ? 'YES' : 'NO',
    scenario.Discharge_Pressure ? 'YES' : 'NO',
    scenario.Suction_Temperature ? 'YES' : 'NO',
    scenario.Discharge_Temperature ? 'YES' : 'NO',
    scenario.symptom
  ]);

  autoTable(doc, {
    startY: finalY + 5,
    head: [[
      'DIVISION',
      'PROB',
      'RCA',
      'ACTIONS',
      'Flow\nRate',
      'Suction\nPress',
      'Discharge\nPress',
      'Suction\nTemp',
      'Discharge\nTemp',
      'SYMPTOM'
    ]],
    body: rcaTableData,
    theme: 'grid',
    headStyles: {
      fillColor: [68, 114, 196],
      textColor: [255, 255, 255],
      fontSize: 7,
      halign: 'center',
      valign: 'middle'
    },
    bodyStyles: { fontSize: 6, cellPadding: 2 },
    columnStyles: {
      0: { cellWidth: 22, halign: 'center' },  // DIVISION
      1: { cellWidth: 12, halign: 'center' },  // PROB
      2: { cellWidth: 55 },                     // RCA
      3: { cellWidth: 55 },                     // ACTIONS
      4: { cellWidth: 12, halign: 'center' },  // Flow Rate
      5: { cellWidth: 12, halign: 'center' },  // Suction Press
      6: { cellWidth: 12, halign: 'center' },  // Discharge Press
      7: { cellWidth: 12, halign: 'center' },  // Suction Temp
      8: { cellWidth: 12, halign: 'center' },  // Discharge Temp
      9: { cellWidth: 45 }                      // SYMPTOM
    },
    didDrawCell: (data) => {
      // Color code divisions
      if (data.section === 'body' && data.column.index === 0) {
        const division = data.cell.text[0];
        let color: [number, number, number] = [255, 255, 255];

        if (division === 'INSTRUMENT') color = [220, 230, 241];
        else if (division === 'PROCESS') color = [226, 239, 218];
        else if (division === 'MECHANICAL') color = [252, 228, 214];
        else if (division === 'ELECTRICAL') color = [255, 242, 204];

        doc.setFillColor(...color);
        doc.rect(data.cell.x, data.cell.y, data.cell.width, data.cell.height, 'F');
        doc.setTextColor(0, 0, 0);
        doc.text(data.cell.text, data.cell.x + data.cell.padding('left'), data.cell.y + data.cell.height / 2, {
          baseline: 'middle'
        });
      }
    }
  });

  // Footer
  // @ts-ignore
  finalY = doc.lastAutoTable.finalY + 10;
  doc.setFontSize(7);
  doc.setTextColor(100, 100, 100);
  const footerText = `Generated by: GUARD (Generative Understanding for Anomaly Response & Detection) | Date: ${new Date().toISOString().replace('T', ' ').substring(0, 19)} | Scenarios Evaluated: ${scenariosToShow.length}`;
  doc.text(footerText, doc.internal.pageSize.getWidth() / 2, doc.internal.pageSize.getHeight() - 10, { align: 'center' });

  // Convert to Buffer
  const pdfOutput = doc.output('arraybuffer');
  return Buffer.from(pdfOutput);
}

export async function POST(request: NextRequest) {
  try {
    const { anomalies } = await request.json();

    // Handle both single anomaly (legacy) and batch
    const anomalyList = Array.isArray(anomalies) ? anomalies : [anomalies];

    // Check if email configuration exists (using main .env variables)
    const smtpServer = process.env.SMTP_SERVER;
    const smtpPort = process.env.SMTP_PORT;
    const smtpUser = process.env.SMTP_USERNAME;
    const smtpPassword = process.env.SMTP_PASSWORD;
    const alertFrom = process.env.ALERT_FROM;
    const alertTo = process.env.ALERT_TO;

    if (!smtpServer || !smtpUser || !smtpPassword || !alertTo) {
      return NextResponse.json(
        { error: 'Email configuration not found in .env' },
        { status: 400 }
      );
    }

    // Create transporter (note: createTransport not createTransporter)
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

    // Build summary table for all anomalies
    const sensors = {
      Flow_Rate: { tag: 'FI1001B', unit: 'MMSCFD', low: 45, high: 56 },
      Suction_Pressure: { tag: 'PI1001B', unit: 'barg', low: 33, high: 34 },
      Discharge_Pressure: { tag: 'PI1004B', unit: 'barg', low: 60, high: 63.3 },
      Suction_Temperature: { tag: 'TI1003B', unit: '°C', low: 90, high: 100 },
      Discharge_Temperature: { tag: 'TI1004B', unit: '°C', low: 189, high: 205 },
    };

    const anomalySummaryRows = anomalyList.map((anomalyData, index) => {
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

    // Email content matching Python version
    const emailHtml = `
      <!DOCTYPE html>
      <html>
      <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
      </head>
      <body style="margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;">
        <div style="max-width: 800px; margin: 0 auto; background-color: #ffffff;">

          <!-- Header -->
          <div style="background-color: #1976d2; color: white; padding: 20px;">
            <h1 style="margin: 0; font-size: 18px; font-weight: 500;">
              [CPP Donggi] ANOMALY DETECTION - BOOSTER COMPRESSOR B CPP DONGGI
            </h1>
            <p style="margin: 8px 0 0 0; font-size: 12px; opacity: 0.9;">
              GUARD (Generative Understanding for Anomaly Response & Detection)
            </p>
          </div>

          <!-- Content -->
          <div style="padding: 24px;">

            <p style="color: #333; line-height: 1.6; margin-bottom: 24px;">
              An abnormal condition has been detected in the process parameters of the
              <strong>BOOSTER COMPRESSOR B CPP DONGGI</strong>. The details are as follows:
            </p>

            <!-- Batch Summary (if multiple anomalies) -->
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

            <!-- Anomaly Details -->
            <h2 style="color: #333; font-size: 20px; margin-bottom: 16px; margin-top: 32px;">
              Anomaly Details
            </h2>

            <table style="width: 100%; border-collapse: collapse; margin-top: 16px; background-color: #fafafa;">
              <thead>
                <tr style="background-color: #e0e0e0;">
                  <th style="padding: 12px; text-align: center; font-weight: 600; border-bottom: 2px solid #bdbdbd; width: 50px;">
                    #
                  </th>
                  <th style="padding: 12px; text-align: left; font-weight: 600; border-bottom: 2px solid #bdbdbd;">
                    Timestamp
                  </th>
                  <th style="padding: 12px; text-align: right; font-weight: 600; border-bottom: 2px solid #bdbdbd;">
                    Threshold ratio
                  </th>
                  <th style="padding: 12px; text-align: left; font-weight: 600; border-bottom: 2px solid #bdbdbd;">
                    Asset integrity status
                  </th>
                </tr>
              </thead>
              <tbody>
                ${anomalySummaryRows}
              </tbody>
            </table>

            <p style="color: #666; font-size: 12px; margin-top: 16px; font-style: italic;">
              *Each anomaly has a detailed PDF report attached with variable analysis and root cause scenarios.
            </p>

            <!-- Footer -->
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

    // Generate PDF attachments for all anomalies
    const pdfAttachments = await Promise.all(
      anomalyList.map(async (anomalyData, index) => {
        const pdfBuffer = await generateRCAPDF(anomalyData);
        const timestampStr = new Date(anomalyData.datetime).toISOString().replace(/:/g, '-').substring(0, 19);
        const pdfFilename = `RCA_Report_${index + 1}_${timestampStr}.pdf`;

        return {
          filename: pdfFilename,
          content: pdfBuffer,
          contentType: 'application/pdf'
        };
      })
    );

    // Send email with all PDF attachments
    const subject = anomalyList.length > 1
      ? `🚨 GUARD BATCH ALERT - ${anomalyList.length} Anomalies Detected`
      : `🚨 GUARD ANOMALY ALERT - ${new Date(firstAnomaly.datetime).toLocaleString()}`;

    await transporter.sendMail({
      from: `"GUARD Alert System" <${alertFrom || smtpUser}>`,
      to: alertTo,
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
    // Return detailed error information
    const errorMessage = error?.message || error?.toString() || 'Failed to send email';
    return NextResponse.json(
      {
        error: errorMessage,
        details: error?.code || error?.response || 'Unknown error'
      },
      { status: 500 }
    );
  }
}

export const dynamic = 'force-dynamic';
