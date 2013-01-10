<section id="sidebar">
    <h2>Menu</h2>
    <div class="widget">
        <h2>Last pages</h2>
        <ul>
            {{list src=pages num=5}}
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
            {{list src=pages num=6 cat=blog}}
                <li>
                    <a title="{{title}}" href="{{permalink}}">
                        {{date}} - {{title}}
                    </a>
                </li>
            {{end}}
        </ul>
    </div>
</section>