<section id="sidebar">
    <h2>Menu</h2>
    <div class="widget">
        <h2>Last pages</h2>
        <ul>
            {{list pages 5}}
                <li>
                    <a title="{{title}}" href="{{permalink}}">
                        {{date}} - {{title}}
                    </a>
                </li>
            {{end}}
        </ul>
    </div>
    <div class="widget">
        <h2>Last posts in blog</h2>
        <ul>
            {{list pages 6 blog}}
                <li>
                    <a title="{{title}}" href="{{permalink}}">
                        {{date}} - {{title}}
                    </a>
                </li>
            {{end}}
        </ul>
    </div>
</section>