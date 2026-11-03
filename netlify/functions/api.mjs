import {getStore} from '@netlify/blobs';
import {handler} from '../../server/api.mjs';
export default req=>handler(getStore({name:'vcu-session-02',consistency:'strong'}))(req);
