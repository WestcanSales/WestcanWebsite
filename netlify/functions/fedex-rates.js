// Netlify serverless function — FedEx live parcel rates.
// Holds credentials server-side (env vars); browser never sees them.
// Routes by destination country: US dest -> US account, origin Blaine WA;
// CA dest -> CA account, origin Langley BC.

const ORIGINS = {
  us: { postalCode: '98230', countryCode: 'US', stateOrProvinceCode: 'WA' },
  ca: { postalCode: 'V2Z2A9', countryCode: 'CA', stateOrProvinceCode: 'BC' },
};

// Box profile: 4 trays per box, 20 lb, 22x14x18 in
const BOX = { weight: 20, length: 22, width: 14, height: 18, traysPer: 4 };

async function getToken(clientId, clientSecret) {
  const res = await fetch('https://apis.fedex.com/oauth/token', {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: new URLSearchParams({
      grant_type: 'client_credentials',
      client_id: clientId,
      client_secret: clientSecret,
    }),
  });
  if (!res.ok) throw new Error('oauth ' + res.status);
  return (await res.json()).access_token;
}

exports.handler = async (event) => {
  const cors = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Access-Control-Allow-Methods': 'POST, OPTIONS',
    'Content-Type': 'application/json',
  };
  if (event.httpMethod === 'OPTIONS') return { statusCode: 200, headers: cors, body: '' };
  if (event.httpMethod !== 'POST') return { statusCode: 405, headers: cors, body: '{"error":"POST only"}' };

  try {
    const { country, postalCode, stateCode, trays } = JSON.parse(event.body || '{}');
    const c = (country || '').toLowerCase();
    if (!['us', 'ca'].includes(c)) throw new Error('country must be us or ca');
    if (!postalCode) throw new Error('postalCode required');
    const nTrays = Math.max(BOX.traysPer, Math.ceil((parseInt(trays) || BOX.traysPer) / BOX.traysPer) * BOX.traysPer);
    const boxes = nTrays / BOX.traysPer;

    const clientId = process.env.FEDEX_CA_CLIENT_ID;
    const clientSecret = process.env.FEDEX_CA_CLIENT_SECRET;
    const accountNumber = c === 'us' ? process.env.FEDEX_US_ACCOUNT : process.env.FEDEX_CA_ACCOUNT;
    if (!clientId || !clientSecret) throw new Error('missing FEDEX_CA_CLIENT_ID / FEDEX_CA_CLIENT_SECRET');
    if (!accountNumber) throw new Error('missing account number for ' + c);

    const token = await getToken(clientId, clientSecret);
    const origin = ORIGINS[c];

    const packages = Array.from({ length: boxes }, () => ({
      weight: { units: 'LB', value: BOX.weight },
      dimensions: { length: BOX.length, width: BOX.width, height: BOX.height, units: 'IN' },
    }));

    const payload = {
      accountNumber: { value: accountNumber },
      requestedShipment: {
        shipper: { address: origin },
        recipient: {
          address: {
            postalCode: String(postalCode).replace(/\s/g, ''),
            countryCode: c.toUpperCase(),
            ...(stateCode ? { stateOrProvinceCode: stateCode } : {}),
          },
        },
        pickupType: 'DROPOFF_AT_FEDEX_LOCATION',
        rateRequestType: ['ACCOUNT', 'LIST'],
        requestedPackageLineItems: packages,
      },
    };

    const res = await fetch('https://apis.fedex.com/rate/v1/rates/quotes', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: 'Bearer ' + token,
        'X-locale': c === 'ca' ? 'en_CA' : 'en_US',
      },
      body: JSON.stringify(payload),
    });
    const data = await res.json();
    if (!res.ok) {
      return { statusCode: 502, headers: cors,
        body: JSON.stringify({ error: 'fedex', detail: data.errors || data }) };
    }

    // Normalize: one entry per service with the account (or list) total
    const services = (data.output?.rateReplyDetails || []).map((s) => {
      const shipmentDetail =
        (s.ratedShipmentDetails || []).find((d) => d.rateType === 'ACCOUNT') ||
        (s.ratedShipmentDetails || [])[0] || {};
      return {
        service: s.serviceName || s.serviceType,
        serviceType: s.serviceType,
        amount: shipmentDetail.totalNetCharge,
        currency: shipmentDetail.currency || (c === 'ca' ? 'CAD' : 'USD'),
        transit: s.commit?.dateDetail?.dayFormat || s.commit?.derivedTransitTime || null,
      };
    }).filter((x) => x.amount != null).sort((a, b) => a.amount - b.amount);

    return { statusCode: 200, headers: cors,
      body: JSON.stringify({ boxes, trays: nTrays, country: c, services }) };
  } catch (err) {
    return { statusCode: 500, headers: cors, body: JSON.stringify({ error: String(err.message || err) }) };
  }
};
