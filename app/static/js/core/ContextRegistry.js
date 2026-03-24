// PageRegistry.js
export const ContextRegistry = {
    _ctx: new Map(),

    register(ctxName, ctx) { 
        this._ctx.set(ctxName, ctx); 
        console.log('PageRegistry. ctxName: ', ctxName, '\nctx: ', ctx, '\n_ctx: ', this._ctx);
    },
    get(ctxName) { return this._ctx.get(ctxName); }
};
